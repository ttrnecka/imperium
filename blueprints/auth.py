import os
from flask import Blueprint, render_template, abort, session, redirect, url_for, request
from flask import current_app as app
from requests_oauthlib import OAuth2Session

auth = Blueprint('auth', __name__)

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

@auth.record
def record_auth(setup_state):
    config = setup_state.app.config
    if 'http://' in config["OAUTH2_REDIRECT_URI"]:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

def token_updater(token):
    """token_updater"""
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    """make_session"""
    return OAuth2Session(
        client_id=app.config["OAUTH2_CLIENT_ID"],
        token=token,
        state=state,
        scope=scope,
        redirect_uri=app.config["OAUTH2_REDIRECT_URI"],
        auto_refresh_kwargs={
            'client_id': app.config["OAUTH2_CLIENT_ID"],
            'client_secret': app.config["SECRET_KEY"],
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@auth.route('/signin')
def signin():
    """sign using discord OAUTH"""
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@auth.route('/signout')
def signout():
    """sign using discord OAUTH"""
    session.pop('oauth2_state', None)
    session.pop('oauth2_token', None)
    session.pop('discord_user', None)
    return redirect('/')

@auth.route('/callback')
def callback():
    """discord callback target"""
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=app.config["SECRET_KEY"],
        authorization_response=request.url)
    session['oauth2_token'] = token
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()

    session['discord_user'] = user
    return redirect("/")
    