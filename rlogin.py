import praw
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

def get_auth_r(username, app_name, version='1.0', uas=None):
    # Fail silently if local app lookup fails
    try:
        client_id, client_secret, _ = find_app_info(app_name)
        password = find_pw(username)
    except FileNotFoundError:
        client_id = None
    except StopIteration:
        client_id = None
    if uas == None:
        uas = "Windows:{0}:{1} by {2}, id={3}".format(app_name, version, username, client_id)
    r = praw.Reddit(user_agent=uas, client_id=client_id, client_secret=client_secret, username=username, password=password)
    return r