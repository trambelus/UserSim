import praw
import ftplib
import requests

PW_FILE = 'pw.txt'
SEC_FILE = 'secrets.txt'

def find_pw(username):
	with open(PW_FILE,'r') as f:
		stuff = f.readlines()
		try:
			ret = next(x[1] for x in [t.split('\t') for t in stuff] if x[0] == username).rstrip()
		except StopIteration:
			raise LookupError("User not found: %s" % username)
		return ret

# -- OAuth stuff

def find_app_info(app_name):
	with open(SEC_FILE, 'r') as f:
		stuff = f.readlines()
		try:
			ret = [i.rstrip() for i in next(x[1:] for x in [t.split('\t') for t in stuff] if x[0] == app_name)]
		except StopIteration:
			raise LookupError("App not found: %s" % app_name)
		return ret

def set_auth(r, app_name, username, version):
	[client_id, client_secret, redirect_uri] = find_app_info(app_name)
	password = find_pw(username)
	client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
	post_data = {"grant_type": "password", "username": username, "password": password, "duration": "permanent"}
	headers = {"User-Agent": "{0}/{1} by {2}".format(app_name, version, username)}
	response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
	#print(response.json())
	token = response.json()['access_token']
	r.set_oauth_app_info(client_id, client_secret, redirect_uri)
	r.set_access_credentials({'flair','privatemessages','submit'}, token)
	return token

def get_auth_r(username, app_name, version, uas=None):
	[client_id, _, _] = find_app_info(app_name)
	if uas == None:
		uas = "Windows:{0}:{1} by {2}, id={3}".format(app_name, version, username, client_id)
	r = praw.Reddit(uas)
	set_auth(r, app_name, username, version)
	return r