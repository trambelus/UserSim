#!/usr/bin/env python3
"""
    TODO:
     * Reduce the effects of user error
     	- Levenshtein distance for username typos (did you mean...?)
     	- Missing + in simple requests
     	- /u/UserSimulator
     * Subreddit simulation (+/u/User_Simulator /r/someplace)
     * Customization options (command flags)
     * Change backend to SQLite cache
     * Ease restrictions on sentence filter
     Maybe:
     * Read self text, not just comments
     * PM replies
     * Comment score incorporation (trigram scoring?)
     * Random simulation (+/u/User_Simulator *)
     * Friend guessing (+/u/User_Simulator /u/somebody's friends)
"""

USER = 'User_Simulator'
APP = 'Simulator'
VERSION = '1.9.9'

import sys
import contextlib

# These were stolen from StackOverflow
# Gotta cut down on console clutter
class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostderr():
    save_stderr = sys.stderr
    sys.stderr = DummyFile()
    yield
    sys.stderr = save_stderr

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

@contextlib.contextmanager
def silent():
	with nostdout():
		with nostderr():
			yield


def getch():
    """
    Get a single character from standard input.

    Returns:
    bytes/str (python2) with that character.
    """
    import platform
    if platform.system() == 'Windows':
        import msvcrt
        return msvcrt.getch()
    else:
        # it's a Unix system!
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode()

import markovify
import re
import praw
import multiprocessing as mp
import time
import rlogin
from unidecode import unidecode
import os
import os.path
import string
import warnings
import nltk
import random
import tempfile

LIMIT = 1000 # Max comments to pull from user history

USERMOD_DIR = tempfile.gettempdir()  # Cache directory

MIN_COMMENTS = 25	# Users with less than this number of comments won't be attempted.
# The Markov chains usually turn out a lot worse with less input.
# TODO: detect the entropy or uniqueness of the corpus instead of raw length.
# Anyone who knows a good way to do this, PM /u/Trambelus if you like.

TRIES = 1000 # Max number of times to try each comment generation

MONITOR_PROCESSES = 1
INBOX_LIMIT = 1000*MONITOR_PROCESSES # Max mentions to pull from inbox

NO_REPLY = ['trollabot','ploungersimulator']
STATE_SIZE = 2
LOGFILE = 'usim.log'
NAMEFILE = 'names.log'
BANNED_FILE = 'banned.txt'

INFO_URL = 'https://github.com/trambelus/UserSim'
SUB_URL = '/r/User_Simulator'
SRC_URL = 'https://github.com/trambelus/UserSim/blob/master/usim.py'

REFRESH_THRESHOLD = 2*24*60*60

def get_footer():
	return '\n\n-----\n\n[^^Info](%s) ^^| [^^Subreddit](%s)' % (INFO_URL, SUB_URL)


def log(*msg, file=None, additional='', console_only=False):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	if file:
		print(output, file=file)
	else:
		print(output + additional)
		if not console_only:
			with open(LOGFILE, 'a') as f:
				f.write(output + '\n')

class PText(markovify.Text):
	"""
	This subclass makes three changes: it modifies the sentence filter
	to allow emotes in comments, it uses the Natural Language Toolkit
	for slightly more coherent responses, and it guarantees a response
	every time with make_sentence.
	"""
	def test_sentence_input(self, sentence):
		"""
		A basic sentence filter. This one rejects sentences that contain
		the type of punctuation that would look strange on its own
		in a randomly-generated sentence. 
		"""
		emote_pat = re.compile(r"\[.+?\]\(\/.+?\)")
		reject_pat = re.compile(r"(^')|('$)|\s'|'\s|([\"(\(\)\[\])])|(github.com/trambelus/UserSim)|(/r/User_Simulator)|(~\ [\w\d\-_]{3,20}\ -----)")
		# Decode unicode, mainly to normalize fancy quotation marks
		decoded = unidecode(sentence)
		# Sentence shouldn't contain problematic characters
		filtered_str = re.sub(emote_pat, '', decoded).replace('  ',' ')
		# Filtered sentence will have neither emotes nor double spaces
		if re.search(reject_pat, filtered_str):
			# Not counting emotes, there are no awkward characters.
			return False
		if filtered_str in get_footer():
			return False
		return True

	# def make_sentence(self, *args, **kwargs):
	# 	for i in range(TRIES):
	# 		ret = super(PText, self).make_sentence(*args, **kwargs)
	# 		if ret == None:
	# 			return None
	# 		if ('/u/%s' % USER).lower() not in ret.lower():
	# 			return ret
	# 	return None

	if 'nltk' in globals(): # So it doesn't die if I comment out the nltk import
		def word_split(self, sentence):
			words = re.split(self.word_split_pattern, sentence)
			words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
			return words
		def word_join(self, words):
			sentence = " ".join(word.split("::")[0] for word in words)
			return sentence

def get_history(r, user, limit=LIMIT, subreddit=None):
	"""
	Grabs a user's most recent comments and returns them as a single string.
	The average will probably be 20k-30k words.
	"""
	try:
		redditor = r.get_redditor(user)
		comments = redditor.get_comments(limit=limit)
		c_finished = False
		while not c_finished:
			body = []
			total_sentences = 0
			recursion_testing = True
			try:
				for c in comments:
					if ('+/u/%s' % USER.lower()) not in c.body.lower():
						recursion_testing = False
					if (not c.distinguished) and ((not subreddit) or c.subreddit.display_name == subreddit):
						body.append(c.body)
						try:
							total_sentences += len(markovify.split_into_sentences(c.body))
						except Exception:
							# Ain't no way I'm letting a little feature like this screw up my processing, no matter what happens
							total_sentences += 1
				c_finished = True
			except praw.errors.HTTPException as ex:
				log(str(ex))
				pass
			except praw.errors.NotFound as ex:
				break
		num_comments = len(body)
		if num_comments >= MIN_COMMENTS and recursion_testing:
			return (0, 0, 0)
		sentence_avg = total_sentences / num_comments if num_comments > 0 else 0
		body = ' '.join(body)
		return (body, num_comments, sentence_avg)
	except praw.errors.NotFound:
		return (None, None, None)

def levenshteinDistance(s1,s2):
	if len(s1) > len(s2):
		s1,s2 = s2,s1
	distances = range(len(s1) + 1)
	for index2,char2 in enumerate(s2):
		newDistances = [index2+1]
		for index1,char1 in enumerate(s1):
			if char1 == char2:
				newDistances.append(distances[index1])
			else:
				newDistances.append(1 + min((distances[index1],
											 distances[index1+1],
											 newDistances[-1])))
		distances = newDistances
	return distances[-1]

def get_markov(r, id, user):
	"""
	Given a user, return a Markov state model for them,
	either from the cache or fresh from reddit via praw.
	"""
	txt_fname = os.path.join(USERMOD_DIR, '%s.txt' % user)
	json_fname = os.path.join(USERMOD_DIR, '%s.json' % user)
	info_fname = os.path.join(USERMOD_DIR, '%s.info' % user)
	# Stores two files: some-reddit-user.txt for the raw corpus,
	# and some-reddit-user.json for the structure holding the Markov state model.
	def from_cache():
		#log("%s: Reading cache for %s" % (id, user))
		mod_time = os.path.getmtime(txt_fname)
		if time.time() - mod_time > REFRESH_THRESHOLD:
			log("Refreshing info for %s" % user, console_only=True)
			return from_scratch()
		f_txt = open(txt_fname, 'r')
		f_json = open(json_fname, 'r')
		f_info = open(info_fname, 'r')
		text = ''.join(f_txt.readlines())
		json = f_json.readlines()[0]
		try:
			sentence_avg = int(f_info.readlines()[0])
		except ValueError:
			sentence_avg = 1
		if text == '' or json == []:
			return from_scratch()
		f_txt.close()
		f_json.close()
		return (PText(text, state_size=STATE_SIZE, chain=markovify.Chain.from_json(json)), sentence_avg)

	def from_scratch():
		# No cache was found: build the model from scratch
		#log("%s: Getting history for %s" % (id, user))
		(history, num_comments, sentence_avg) = get_history(r, user)
		if history == None:
			return ("User '%s' not found.", 0)
		if history == 0:
			log('User %s is attempting recursion' % user)
			return ("I see what you're trying to do, %s. It won't work.", 0)
		if num_comments < MIN_COMMENTS:
			return ("User '%%s' has %d comment%s in history; minimum requirement is %d." % (num_comments,'' if num_comments == 1 else 's', MIN_COMMENTS), 0)
		#log("%s: Building model for %s" % (id, user))
		try:
			model = PText(history, state_size=STATE_SIZE)
		except IndexError:
			return ("Error: User '%s' is too dank to simulate.", 0)
		f = open(txt_fname, 'w')
		f.write(unidecode(history))
		f.close()
		f = open(json_fname, 'w')
		f.write(model.chain.to_json())
		f.close()
		f = open(info_fname, 'w')
		f.write(str(int(sentence_avg)))
		f.close()
		return (model, int(sentence_avg))

	if os.path.isfile(txt_fname) and os.path.isfile(json_fname) and os.path.isfile(info_fname):
		return from_cache()
	else:
		return from_scratch()

def try_reply(com, msg):
	try:
		if USER.lower() in [rep.author.name.lower() for rep in com.replies if rep.author != None]:
			return
	except Exception:
		pass
	newcom = com.reply(msg)
	# q.put(com.name)
	try:
		with open(NAMEFILE, 'a') as f:
			f.write(newcom.name + '\n')
	except Exception:
		pass

def dfmt(created_utc):
	return time.strftime("%Y-%m-%d %X",time.localtime(created_utc))

def process(q, com, val, index):
	"""
	Multiprocessing target. Gets the Markov model, uses it to get a sentence, and posts that as a reply.
	"""
	warnings.simplefilter('ignore')
	if com == None:
		return
	id = com.name
	author = com.author.name if com.author else '[deleted]'
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, operating on behalf of %s" % (VERSION,author))
	com = r.get_info(thing_id=id)
	sub = com.subreddit.display_name
	ctime = time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc))
	val = val.replace('\n',' ')
	val = val.replace('\t',' ')
	val = val.replace(chr(160),' ')
	target_user = val[val.rfind(' ')+1:].strip()
	if author.lower() in NO_REPLY:
		try_reply(com,"I see what you're trying to do.%s" % get_footer())
		return
	if ('+/u/%s' % USER).lower() in target_user.lower():
		try_reply(com,"User '%s' appears to have broken the bot. That is not nice, %s.%s" % (author,author,get_footer()))
		return
	idx = com.body.lower().find(target_user.lower())
	target_user = com.body[idx:idx+len(target_user)]
	r_subreddit = re.compile(r"/?r/[\w\d_]{0,21}")
	if target_user[:3] == '/u/':
		target_user = target_user[3:]
	if target_user == 'YOURUSERNAMEHERE':
		log("Corrected 'YOURUSERNAMEHERE' to %s" % author)
		target_user = author
	#log('%s: Started %s for %s on %s' % (id, target_user, author, time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc))))
	try:
		next(r.get_redditor(target_user).get_comments(limit=1))
	except praw.errors.NotFound:
		if levenshteinDistance(target_user, author) <3:
			log("Corrected spelling from %s to %s" % (target_user, author))
			target_user = author
	except StopIteration:
		pass
	except praw.errors.HTTPException:
		time.sleep(1)
	(model, sentence_avg) = get_markov(r, id, target_user)
	try:
		if isinstance(model, str):
			try_reply(com,(model % target_user) + get_footer())
			log('%s: (%d) %s by %s in %s on %s:\n%s' % (id, index, target_user, author, sub, ctime, model % target_user), additional='\n')
		else:
			if sentence_avg == 0:
				try_reply(com,"Couldn't simulate %s: maybe this user is a bot, or has too few unique comments.%s" % (target_user,get_footer()))
				return
			reply_r = []
			for _ in range(random.randint(1,sentence_avg)):
				tmp_s = model.make_sentence(tries=TRIES)
				if tmp_s == None:
					try_reply(com,"Couldn't simulate %s: maybe this user is a bot, or has too few unique comments.%s" % (target_user,get_footer()))
					return
				reply_r.append(tmp_s)
			reply_r = ' '.join(reply_r)
			reply = unidecode(reply_r)
			if com.subreddit.display_name == 'EVEX':
				target_user = target_user + random.choice(['-senpai','-kun','-chan','-san','-sama'])
			log('%s: (%d) %s (%d) by %s in %s on %s, reply' % (id, index, target_user, sentence_avg, author, sub, ctime), additional='\n%s\n' % reply)
			target_user = target_user.replace('_','\_')
			try_reply(com,'%s\n\n ~ %s%s' % (reply,target_user,get_footer()))
		#log('%s: Finished' % id)
	except praw.errors.RateLimitExceeded as ex:
		log("%s: (%d) %s (%d) by %s in %s on %s: rate limit exceeded: %s" % (id, index, target_user, sentence_avg, author, sub, ctime, str(ex)))
		q.put(id)
	except praw.errors.Forbidden as ex:
		log("Could not reply to comment by %s in %s: %s" % (author, sub, str(ex)))
	except praw.errors.APIException:
		log("Parent comment by %s in %s was deleted" % (author, sub))
	except praw.errors.HTTPException:
		log("%s: (%d) %s (%d) by %s in %s on %s: could not reply, will retry: %s" % (id, index, target_user, sentence_avg, author, sub, ctime, str(ex)))
		q.put(id)

def monitor_sub(q, index):

	started = []
	with open(BANNED_FILE, 'r') as f:
		banned = [s.rstrip() for s in f.readlines()]
	get_r = lambda: rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, main thread %d" % (VERSION, index))
	req_pat = re.compile(r"\+(\s)?/u/%s\s?(\[.\])?\s+(/u/)?[\w\d\-_]{3,20}" % USER.lower())
	with silent():
		r = get_r()
	t0 = time.time()
	log('Started main thread %d' % (index+1))
	while True:
		try:
			# Every 55 minutes, refresh the login.
			if (time.time() - t0 > 55*60):
				with silent():
					r = get_r()
				log("Refreshed login for thread %d" % (index+1))
				t0 = time.time()
			mentions = r.get_inbox(limit=INBOX_LIMIT)
			for com in mentions:
				if int(com.name[3:], 36) % MONITOR_PROCESSES != index: 
					continue # One of the other monitor threads is handling this one; skip
				if com.name in started:
					continue # We've already started on this one, move on
				started.append(com.name)
				try:
					if com.subreddit == None:
						continue
					if com.subreddit.display_name in banned:
						log("%s: (%d) Ignored request from banned subreddit %s" % (com.name,index+1,com.subreddit.display_name))
						continue
				except praw.errors.Forbidden:
					continue
				res = re.search(req_pat, com.body.lower())
				if res == None:
					continue # We were mentioned but it's not a proper request, move on
				try:
					if USER.lower() in [rep.author.name.lower() for rep in com.replies if rep.author != None]:
						continue # We've already hit this one, move on
				except praw.errors.Forbidden:
					continue
				
				warnings.simplefilter("ignore")
				try:
					mp.Process(target=process, args=(q, com, res.group(0), index+1)).start()
				except Exception:
					continue
			while q.qsize() > 0:
				item = q.get()
				if item == 'clear':
					log("Clearing list of started tasks")
					started = []
				elif item == 'quit':
					log("Stopping main process")
					return
				elif item in started:
					started.remove(item)
		except praw.errors.InvalidComment:
			continue # This one was completely trashing the console, so handle it silently.
		except AssertionError:
			with silent():
				r = get_r()
		# General-purpose catch to make the script unbreakable.
		except Exception as ex:
			log(str(index+1) + ": " + str(type(ex)) + ": " + str(ex))
			time.sleep(1)

def monitor():
	"""
	Main loop. Looks through username notifications, comment replies, and whatever else,
	and launches a single process for every new request it finds.
	"""
	q = mp.Queue()
	quit_proc = mp.Process(target=wait, args=(q,))
	quit_proc.start()
	for i in range(MONITOR_PROCESSES):
		mp.Process(target=monitor_sub, args=(q,i)).start()
	
def wait(q):
	"""
	Separate thread for responding if the operator presses command keys
	q = quit
	c = clear 'started' list, in case of an error in a processing script
	"""
	while True:
		inp = getch()
		if inp == b'q':
			log("Quit")
			q.put('quit')
			break
		if inp == b'c':
			q.put('clear')

def manual(user, num):
	"""
	This allows the script to be invoked like this:
	usim.py manual some-reddit-user
	This was useful for when the script failed to reply in some cases.
	I logged in as the script, got a manual response like this,
	and just pasted it in as a normal comment.
	They never knew.
	Don't tell them.
	"""
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, operating in manual mode" % VERSION)
	(model, sentence_avg) = get_markov(r, 'manual', user)
	for i in range(sentence_avg):
		log(unidecode(model.make_sentence()))

def count(user):
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, counting comments of %s" % (VERSION,user))
	(history, num_comments, sentence_avg) = get_history(r, user)
	print("{}: {} comments, average {:.3f} sentences per comment".format(user, num_comments, sentence_avg))

def upgrade():
	files = [f[:-4] for f in os.listdir(USERMOD_DIR) if f[-4:] == '.txt']
	r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, upgrading cache" % VERSION)
	for user in files:
		info_fname = os.path.join(USERMOD_DIR, user + '.info')
		if os.path.isfile(info_fname):
			continue
		(history, num_comments, sentence_avg) = get_history(r, user)
		print("%s: average %d across %d comments" % (user, int(sentence_avg), num_comments))
		with open(info_fname, 'w') as f:
			f.write(str(int(sentence_avg)))

def get_user_top(sort):
	r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, updating local user cache" % VERSION)
	redditor = r.get_redditor(USER)
	comments = redditor.get_comments(limit=None, sort=sort)
	for c in comments:
		print("%s at %s in %s: %s" % (c.name, dfmt(c.created_utc), c.subreddit.display_name, c.score))
		with open("%s.txt" % sort,"a") as f:
			f.write(c.name + '\n')

def open_by_id(id):
	import webbrowser
	r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, updating local user cache" % VERSION)
	webbrowser.open_new_tab(r.get_info(thing_id=id).permalink)

def get_banned():
	r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, updating local user cache" % VERSION)
	with open(BANNED_FILE, 'r') as f:
		banned = [s.rstrip() for s in f.readlines()]
	c = 0
	with open("bancount.txt", 'w') as f:
		for sub in banned:
			try:
				b = r.get_subreddit(sub).subscribers
				c += b
			except praw.errors.Forbidden:
				b = "Unknown"
			f.write("%s: %s\n" % (sub, b))
		f.write("----------------\nTotal: %d" % c)
	print("Banned from %d subs, %d subscribers" % len(banned), c)

if __name__ == '__main__':
	if len(sys.argv) >= 3:
		if sys.argv[1].lower() == 'manual':
			num = 1
			if len(sys.argv) == 4:
				num = int(sys.argv[3])
			manual(sys.argv[2], num)
		elif sys.argv[1].lower() == 'count':
			count(sys.argv[2])
		elif sys.argv[1].lower() == 'names':
			get_user_top(sys.argv[2])
		elif sys.argv[1].lower() == 'link':
			open_by_id(sys.argv[2])
	elif len(sys.argv) > 1:
		if sys.argv[1].lower() == 'upgrade':
			upgrade()
		elif sys.argv[1].lower() == 'banned':
			get_banned()
	else:
		monitor()
