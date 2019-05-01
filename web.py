import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, abort, session, redirect, request, url_for
from flask_migrate import Migrate
from misc.helpers import CardHelper
#from imperiumbase import Coach, Pack
from models.base_model import db
from models.data_models import Coach, Card, Account, Transaction, Tournament
from services import PackService
from models.marsh_models import ma, coach_schema, cards_schema, coaches_schema, tournaments_schema
from sqlalchemy.orm import raiseload
from requests_oauthlib import OAuth2Session

os.environ["YOURAPPLICATION_SETTINGS"] = "config/config.py"

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    db.init_app(app)
    ma.init_app(app)
    return app

app = create_app()
migrate = Migrate(app, db)

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

if 'http://' in app.config["OAUTH2_REDIRECT_URI"]:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
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

@app.route('/signin')
def signin():
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
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
    # store it in session
    session['discord_user'] = user
    return redirect(url_for('.index'))

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route('/me')
def me():
    return jsonify(user=session.get('discord_user',{'code':0}))

@app.route("/")
def index():
    starter_cards = PackService.generate("starter").cards
    return render_template("index.html",starter_cards=starter_cards)

@app.route("/coaches", methods=["GET"])
def get_coaches():
    all_coaches = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).all()
    result = coaches_schema.dump(all_coaches)
    return jsonify(result.data)

@app.route("/tournaments", methods=["GET"])
def get_tournaments():
    all_tournaments = Tournament.query.options(raiseload(Tournament.coaches)).filter_by(status="OPEN").all()
    result = tournaments_schema.dump(all_tournaments)
    return jsonify(result.data)

@app.route("/coaches/<int:coach_id>", methods=["GET"])
def get_coach(coach_id):
    coach = Coach.query.get(coach_id)
    if coach is None:
        abort(404)
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@app.route("/cards/starter", methods=["GET"])
def get_starter_cards():
    starter_cards = PackService.generate("starter").cards
    result = cards_schema.dump(starter_cards)
    return jsonify(result.data)

# run the application
if __name__ == "__main__":
    app.run()
