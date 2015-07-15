#!/usr/bin/env python

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

USER = 'User_Simulator'
APP = 'Simulator'
VERSION = '0.4'

LIMIT = 1000
USERMOD_DIR = 'D:\\usermodels\\'
MIN_COMMENTS = 50	# Users with less than this number of comments won't be attempted.
# The Markov chains usually turn out a lot worse with less input.
# TODO: detect the entropy or uniqueness of the corpus instead of raw length.
# Anyone who knows a good way to do this, PM /u/Trambelus if you like.

USERSET = set(string.ascii_letters+string.digits+'-_')
STATE_SIZE = 2
LOGFILE = 'usim.log'

in_userset = lambda s: all([el in USERSET for el in s])

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
		emote_pat = re.compile(r"\[.*?\]\(\/.+?\)")
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
		for c in comments:
			body.append(c.body)
		num_comments = len(body)
		body = ' '.join(body)
		return (body, num_comments)
	except praw.errors.NotFound:
		return (None, None)

def get_markov(r, id, user):
	"""
	Given a user, return a Markov state model for them,
	either from the cache or fresh from reddit via praw.
	"""
	txt_fname = USERMOD_DIR + '%s.txt' % user
	json_fname = USERMOD_DIR + '%s.json' % user
	# Stores two files: some-reddit-user.txt for the raw corpus,
	# and some-reddit-user.json for the structure holding the Markov state model.
	def from_cache():
		log("%s: Reading cache for %s" % (id, user))
		f_txt = open(txt_fname, 'r')
		f_json = open(json_fname, 'r')
		text = ''.join(f_txt.readlines())
		json = f_json.readlines()[0]
		if text == '' or json == []:
			return from_scratch()
		f_txt.close()
		f_json.close()
		return PText(text, state_size=STATE_SIZE, chain=markovify.Chain.from_json(json))

	def from_scratch():
		# No cache was found: build the model from scratch
		log("%s: Getting history for %s" % (id, user))
		(history, num_comments) = get_history(r, user)
		if history == None:
			log('%s: User %s not found' % (id, user))
			return "User '%s' not found."
		if num_comments < MIN_COMMENTS:
			return "User '%%s' has %d comments in history; minimum requirement is %d." % (num_comments, MIN_COMMENTS)
		log("%s: Building model for %s" % (id, user))
		model = PText(history, state_size=STATE_SIZE)
		f = open(txt_fname, 'w')
		f.write(unidecode(history))
		f.close()
		f = open(json_fname, 'w')
		f.write(model.chain.to_json())
		f.close()
		return model

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
	target_user = val[val.rfind(' ')+1:]
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v0.3 by /u/Trambelus, operating on behalf of %s" % author)
	if target_user[:3] == '/u/':
		target_user = target_user[3:]
	log('%s: started %s for %s on %s' % (id, target_user, author, time.strftime("%Y-%m-%d %X",time.localtime(com.created_utc))))
	model = get_markov(r, id, target_user)
	try:
		if isinstance(model, str):
			com.reply(model % target_user)
		else:
			reply_r = model.make_sentence(tries=100)
			if reply_r == None:
				com.reply("Couldn't simulate %s: maybe this user is a bot, or has too few unique comments." % target_user)
				return
			reply = unidecode(reply_r)
			log("%s: Replying:\n%s" % (id, reply))
			com.reply(reply)
		log('%s: Finished' % id)
	except praw.errors.RateLimitExceeded as ex:
		log(id + ": Rate limit exceeded: " + str(ex))
		q.put(id)

def monitor():
	"""
	Main loop. Looks through username notifications, comment replies, and whatever else,
	and launches a single process for every new request it finds.
	"""
	started = []
	q = mp.Queue()
	quit_proc = mp.Process(target=wait, args=(q,))
	quit_proc.start()
	req_pat = re.compile(r"\+(\s)?/u/%s\s(/u/)?[\w\d\-_]{3,20}" % USER.lower())
	with silent():
		r = rlogin.get_auth_r(USER, APP, VERSION, uas="Windows:User Simulator/v0.3 by /u/Trambelus, main thread")
	t0 = time.time()
	log('Restarted')
	while True:
		try:
			# Every 55 minutes, refresh the login.
			if (time.time() - t0 > 55*60):
				with silent():
					r = rlogin.get_auth_r(USER, APP, VERSION)
				log("Refreshed login")
				t0 = time.time()
			mentions = r.get_inbox()
			for com in mentions:
				if com.author == None:
					continue # Extreme edge case: they deleted their comment before the reply could process
				res = re.search(req_pat, com.body.lower())
				if res == None:
					continue # We were mentioned but it's not a proper request, move on
				if USER.lower() in [rep.author.name.lower() for rep in com.replies if rep.author != None]:
					continue # We've already hit this one, move on
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
		except Exception as ex:
			log("Error in main process: %s" % ex)

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
	model = get_markov(user)
	for i in range(num):
		log(unidecode(model.make_sentence()))

if __name__ == '__main__':
	if len(sys.argv) >= 3 and sys.argv[1].lower() == 'manual':
		num = 1
		if len(sys.argv) == 4:
			num = int(sys.argv[3])
		manual(sys.argv[2], num)
	else:
		monitor()