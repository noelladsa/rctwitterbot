#!/usr/bin/env python3

import os
import json
from functools import wraps

from flask import Flask, session, url_for, flash, redirect, request
from flask import render_template
from flask_oauthlib.client import OAuth

from twitter_updater import TwitterWorker

# flask app and an oauth object  ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

app = Flask(__name__)
app.secret_key = 'dev secret key horses hippos misssspellings etc'
auth = OAuth(app).remote_app(
    'rc twitterer',
    base_url='https://www.recurse.com/api/v1/',
    access_token_url='https://www.recurse.com/oauth/token',
    authorize_url='https://www.recurse.com/oauth/authorize',
    consumer_key=os.environ.get('CONSUMER_KEY', None),
    consumer_secret=os.environ.get('CONSUMER_SECRET', None),
    access_token_method='POST'
    )

updater = TwitterWorker(10800, os.environ.get('CONSUMER_KEY', None),
                        os.environ.get('CONSUMER_SECRET', None),
                        'https://www.recurse.com/api/v1/',
                        'https://www.recurse.com/oauth/token')
# internal auth mechanics ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


def get_login():
    # our internal function to retrieve login data
    # knowledge of session['login'] is only in here, oauth_authorized,
    # and logout
    return session.get('login')


@auth.tokengetter
def get_token(token=None):
    # a decorated tokengetter function is required by the oauth module
    return get_login()['oauth_token']


def protected(route):
    # in large apps it is probably better to use the Flask-Login extension than
    # this route decohttp://10.0.9.205:5000/oauth_authorizedrator because this
    # decorator doesn't provide you with
    # 1. user access levels or
    # 2. the helpful abstraction of an "anonymous" user (not yet logged in)
    @wraps(route)
    def wrapper(*args, **kwargs):
        kwargs.update(login=get_login())
        return route(*args, **kwargs) if kwargs['login'] \
            else redirect(url_for('login', next=request.url))
        # redirect includes "next=request.url" so that after logging in the
        # user will be sent to the page they were trying to access
    return wrapper

# external auth mechanics  ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


@app.route('/login')
def login():
    if get_login():
        flash('You are already logged in.')
        return redirect(request.referrer or url_for('index'))
    else:
        landing = url_for('oauth_authorized',  _external=True)
        return auth.authorize(callback=landing)


@app.route('/oauth_authorized')
@auth.authorized_handler
def oauth_authorized(resp):
    try:
        # make a partial login session here, get the username later
        # if this part works
        # keys into resp are probably different for different oauth providers,
        # unfortunately
        session['login'] = dict(oauth_token=(resp['access_token'],
                                resp['refresh_token']))
        updater.access_token = resp['access_token']
        updater.refresh_token = resp['refresh_token']
    except TypeError as exc:
        flash('The login request was declined.(TypeError: %s)' % exc)
        return redirect(url_for('index'))
    except KeyError as exc:
        flash('There was a problem with the response dict. (KeyError: %s) %s'
              % (exc, resp))
        return redirect(url_for('index'))
    # now get their username
    me = auth.get('people/me')
    if me.status == 200:
        session['login']['user'] = '{first_name} {last_name}'.format(**me.data)
        session['login']['email'] = me.data['email']
        session['login']['image'] = me.data['image']
    else:
        session['login']['user'] = 'Hacker Schooler'

    flash('You are logged in.')
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/get_list')
def get_list():
    return json.dumps(updater.recurser_list)


@app.route('/logout')
def logout():
    # the important bit here is to remove the login from the session
    flash('You have logged out.') if session.pop('login', None) \
        else flash('You aren\'t even logged in.')
    return redirect(url_for('index'))

# pages ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


@app.route('/')
def index():
    return render_template('base.html', login=get_login())


@app.route('/hippos')
@protected
def hippos(login=None):
    return render_template('hippos.html', login=login)


if __name__ == '__main__':
    print "Staring thread"
    updater.start()
    app.debug = True
    app.run(host='0.0.0.0')

# eof
