from httplib2 import Http
from flask import json, abort, request, session, redirect, url_for
from functools import wraps


def validate_token(access_token):
    '''Verifies that an access-token is valid and
    meant for this app.

    Returns None on fail, and an e-mail on success'''
    h = Http()
    resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
                           headers={'Host': 'www.googleapis.com',
                                    'Authorization': 'Bearer ' + str(access_token)})

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    return data['email']


def authorized(fn):
    """Decorator that checks that requests
    contain an id-token in the request header.
    userid will be None if the
    authentication failed, and have an id otherwise.

    Usage:
    @app.route("/")
    @authorized
    def secured_root(userid=None):
        pass
    """
    @wraps(fn)
    def _wrap(*args, **kwargs):
        access_token = session.get('access_token')
        print("Checking token...")
        userid = validate_token(access_token)
        if userid is None:
            print("Check returned FAIL!")
            return redirect(url_for('home'))

        return fn(*args, **kwargs)
    return _wrap
