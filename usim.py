#!/usr/bin/env python

USER = 'User_Simulator'
APP = 'Simulator'
VERSION = '1.6.0'

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

import markovify
import re
with silent():
	import praw
import multiprocessing as mp
import time
import rlogin # I wrote this one (check the repo)
from unidecode import unidecode
import os
import string
import msvcrt
import warnings
with nostderr():
	import nltk
import random

LIMIT = 1000
USERMOD_DIR = 'D:\\usermodels\\'
MIN_COMMENTS = 25	# Users with less than this number of comments won't be attempted.
# The Markov chains usually turn out a lot worse with less input.
# TODO: detect the entropy or uniqueness of the corpus instead of raw length.
# Anyone who knows a good way to do this, PM /u/Trambelus if you like.
TRIES = 1000

NO_REPLY = ['trollabot','ploungersimulator']
STATE_SIZE = 2
LOGFILE = 'usim.log'
INFO_URL = 'https://github.com/trambelus/UserSim'
SUB_URL = '/r/User_Simulator'

def get_footer():
	return '\n\n-----\n\n[^^Info](%s) ^^| [^^Subreddit](%s)' % (INFO_URL, SUB_URL)


def log(*msg, file=None):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join(msg))
	if file:
		print(output, file=file)
	else:
		print(output)
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
		reject_pat = re.compile(r"(^')|('$)|\s'|'\s|([\"(\(\)\[\])])")
		# Decode unicode, mainly to normalize fancy quotation marks
		decoded = unidecode(sentence)
		# Sentence shouldn't contain problematic characters
		filtered_str = re.sub(emote_pat, '', decoded).replace('  ',' ')
		# Filtered sentence will have neither emotes nor double spaces
		if re.search(reject_pat, filtered_str):
			# Not counting emotes, there are no awkward characters.
			return False
		return True
	if 'nltk' in globals(): # So it doesn't die if I comment out the nltk import
		def word_split(self, sentence):
			words = re.split(self.word_split_pattern, sentence)
			words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
			return words
		def word_join(self, words):
			sentence = " ".join(word.split("::")[0] for word in words)
			return sentence

def get_history(r, user, limit=LIMIT):
	"""
	Grabs a user's most recent comments and returns them as a single string.
	The average will probably be 20k-30k words.
	"""
	try:
		redditor = r.get_redditor(user)
		comments = redditor.get_comments(limit=limit)
		body = []
		total_sentences = 0
		recursion_testing = True
		for c in comments:
			if ('+/u/%s' % USER.lower()) not in c.body.lower():
				recursion_testing = False
			if not c.distinguished:
				body.append(c.body)
				try:
					total_sentences += len(markovify.split_into_sentences(c.body))
				except Exception:
					# Ain't no way I'm letting a little feature like this screw up my processing, no matter what happens
					total_sentences += 1
		num_comments = len(body)
		if num_comments > MIN_COMMENTS and recursion_testing:
			return (0, 0, 0)
		sentence_avg = total_sentences / num_comments if num_comments > 0 else 0
		body = ' '.join(body)
		return (body, num_comments, sentence_avg)
	except praw.errors.NotFound:
		return (None, None, None)

def get_markov(r, id, user):
	"""
	Given a user, return a Markov state model for them,
	either from the cache or fresh from reddit via praw.
	"""
	txt_fname = USERMOD_DIR + '%s.txt' % user
	json_fname = USERMOD_DIR + '%s.json' % user
	info_fname = USERMOD_DIR + '%s.info' % user
	# Stores two files: some-reddit-user.txt for the raw corpus,
	# and some-reddit-user.json for the structure holding the Markov state model.
	def from_cache():
		#log("%s: Reading cache for %s" % (id, user))
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
			log('User %s not found' % user)
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

	if os.path.isfile(txt_fname) and os.path.isfile(json_fname):
		return from_cache()
	else:
		return from_scratch()

def process(q, com, val):
	"""
	Multiprocessing target. Gets the Markov model, uses it to get a sentence, and posts that as a reply.
	"""
	warnings.simplefilter('ignore')
	if com == None:
		return
	id = com.name
	author = com.author.name if com.author else 'None'
	sub = com.subreddit.display_name
	val = val.replace('\n',' ')
	val = val.replace('\t',' ')
	val = val.replace(chr(160),' ')
	target_user = val[val.rfind(' ')+1:].strip()
	if author.lower() in NO_REPLY:
		com.reply("I see what you're trying to do.%s" % get_footer())
		return
	if ('+/u/%s' % USER).lower() in target_user.lower():
		com.reply("User '%s' appears to have broken the bot. That is not nice, %s.%s" % (author,author,get_footer()))
		return
	idx = com.body.lower().find(target_user.lower())
	target_user = com.body[idx:idx+len(target_user)]
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, operating on behalf of %s" % (VERSION,author))
	if target_user[:3] == '/u/':
		target_user = target_user[3:]
	#log('%s: Started %s for %s on %s' % (id, target_user, author, time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc))))
	(model, sentence_avg) = get_markov(r, id, target_user)
	try:
		if isinstance(model, str):
			com.reply((model % target_user) + get_footer())
			log('%s by %s in %s on %s:\n%s\n' % (target_user, author, com.subreddit.display_name, time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc)), model % target_user))
		else:
			if sentence_avg == 0:
				com.reply("Couldn't simulate %s: maybe this user is a bot, or has too few unique comments.%s" % (target_user,get_footer()))
				return
			reply_r = []
			for _ in range(random.randint(1,sentence_avg*2)):
				tmp_s = model.make_sentence(tries=TRIES)
				if tmp_s == None:
					com.reply("Couldn't simulate %s: maybe this user is a bot, or has too few unique comments.%s" % (target_user,get_footer()))
					return
				reply_r.append(tmp_s)
			reply_r = ' '.join(reply_r)
			reply = unidecode(reply_r)
			if com.subreddit.display_name == 'EVEX':
				target_user = target_user + random.choice(['-senpai','-kun','-chan','-san','-sama'])
			log('%s (%d) by %s in %s on %s, reply:\n%s\n' % (target_user, sentence_avg, author, sub, time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc)), reply))
			com.reply('%s\n\n ~ %s%s' % (reply,target_user,get_footer()))
		#log('%s: Finished' % id)
	except praw.errors.RateLimitExceeded as ex:
		log(id + ": Rate limit exceeded: " + str(ex))
		q.put(id)
	except praw.errors.Forbidden:
		log("Could not reply to comment by %s in %s" % (author, sub))
	except praw.errors.APIException:
		log("Parent comment by %s in %s was deleted" % (author, sub))

def monitor():
	"""
	Main loop. Looks through username notifications, comment replies, and whatever else,
	and launches a single process for every new request it finds.
	"""
	get_r = lambda: rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, main thread" % VERSION)

	started = []
	q = mp.Queue()
	quit_proc = mp.Process(target=wait, args=(q,))
	quit_proc.start()
	req_pat = re.compile(r"\+(\s)?/u/%s\s?(\[.\])?\s+(/u/)?[\w\d\-_]{3,20}" % USER.lower())
	with silent():
		r = get_r()
	t0 = time.time()
	log('Restarted')
	while True:
		try:
			# Every 55 minutes, refresh the login.
			if (time.time() - t0 > 55*60):
				with silent():
					r = get_r()
				log("Refreshed login")
				t0 = time.time()
			mentions = r.get_inbox()
			for com in mentions:
				res = re.search(req_pat, com.body.lower())
				if res == None:
					continue # We were mentioned but it's not a proper request, move on
				try:
					if USER.lower() in [rep.author.name.lower() for rep in com.replies if rep.author != None]:
						continue # We've already hit this one, move on
				except praw.errors.Forbidden:
					continue
				if com.name in started:
					continue # We've already started on this one, move on
				started.append(com.name)
				warnings.simplefilter("ignore")
				mp.Process(target=process, args=(q, com, res.group(0))).start()
			if not quit_proc.is_alive():
				log("Stopping main process")
				return
			while q.qsize() > 0:
				item = q.get()
				if item == 'clear':
					log("Clearing list of started tasks")
					started = []
				elif item in started:
					started.remove(item)
			time.sleep(1)
		# General-purpose catch to make the script unbreakable.
		except praw.errors.InvalidComment:
			continue # This one was completely trashing the console, so handle it silently.
		except Exception as ex:
			log(str(type(ex)) + ": " + str(ex))

def wait(q):
	"""
	Separate thread for responding if the operator presses command keys
	q = quit
	c = clear 'started' list, in case of an error in a processing script
	"""
	while True:
		inp = msvcrt.getch()
		if inp == b'q':
			log("Quit")
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

def upgrade():
	files = [f[:-4] for f in os.listdir(USERMOD_DIR) if f[-4:] == '.txt']
	r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v%s by /u/Trambelus, upgrading cache" % VERSION)
	for user in files:
		info_fname = USERMOD_DIR + user + '.info'
		if os.path.isfile(info_fname):
			continue
		(history, num_comments, sentence_avg) = get_history(r, user)
		print("%s: average %d across %d comments" % (user, int(sentence_avg), num_comments))
		with open(info_fname, 'w') as f:
			f.write(str(int(sentence_avg)))

if __name__ == '__main__':
	if len(sys.argv) >= 3 and sys.argv[1].lower() == 'manual':
		num = 1
		if len(sys.argv) == 4:
			num = int(sys.argv[3])
		manual(sys.argv[2], num)
	elif len(sys.argv) > 1 and sys.argv[1].lower() == 'upgrade':
		upgrade()
	else:
		monitor()