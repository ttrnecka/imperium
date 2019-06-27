import os
import requests
from datetime import timedelta
from flask import Flask, render_template, jsonify, abort, session, redirect, request, url_for
from flask_fontawesome import FontAwesome
from flask_migrate import Migrate
from misc.helpers import CardHelper
from models.base_model import db
from models.data_models import Coach, Card, Account, Transaction, Tournament, TournamentSignups, Duster, TransactionError, Deck
from services import PackService, TournamentService, RegistrationError, WebHook, DusterService, DustingError, NotificationService, TransactionService, DeckService, DeckError, CoachService, LedgerNotificationService, BB2Service, AchievementNotificationService
from models.marsh_models import ma, coach_schema, cards_schema, coaches_schema, tournaments_schema, tournament_schema, duster_schema, leaderboard_coach_schema, deck_schema
from sqlalchemy.orm import raiseload
from requests_oauthlib import OAuth2Session
from bb2api import Agent
import json

os.environ["YOURAPPLICATION_SETTINGS"] = "config/config.py"
ROOT = os.path.dirname(__file__)

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    db.init_app(app)
    ma.init_app(app)
    fa=FontAwesome(app)
    
    # register wehook as Tournament service notifier
    NotificationService.register_notifier(WebHook(app.config['DISCORD_WEBHOOK_BANK']).send)
    LedgerNotificationService.register_notifier(WebHook(app.config['DISCORD_WEBHOOK_LEDGER']).send)
    AchievementNotificationService.register_notifier(WebHook(app.config['DISCORD_WEBHOOK_ACHIEVEMENTS']).send)
    BB2Service.register_agent(Agent(app.config['BB2_API_KEY']))
    return app

app = create_app()
migrate = Migrate(app, db)

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

store = os.path.join(ROOT, 'data', f"season{app.config['SEASON']}")
stats_file = os.path.join(store,"stats.json")

def get_stats():
  f = open(stats_file, "r")
  data = json.loads(f.read())
  f.close()
  return data

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

def current_user():
    return session['discord_user'] if 'discord_user' in session else None

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

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
    bb2_names = sorted(list(get_stats()['coaches'].keys()))
    return render_template("index.html",bb2_names=bb2_names)

@app.route("/coaches", methods=["GET"])
def get_coaches():
    all_coaches = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).all()
    result = coaches_schema.dump(all_coaches)
    return jsonify(result.data)


@app.route("/coaches/leaderboard", methods=["GET"])
def get_coaches_leaderboard():
    all_coaches = Coach.query.all()
    result={}
    result['coaches'] = leaderboard_coach_schema.dump(all_coaches).data
    result['coach_stats'] = list(get_stats()['coaches'].values())
    return jsonify(result)

@app.route("/tournaments", methods=["GET"])
def get_tournaments():
    all_tournaments = Tournament.query.options(raiseload(Tournament.coaches)).filter(Tournament.status.in_(("OPEN","RUNNING"))).all()
    result = tournaments_schema.dump(all_tournaments)
    return jsonify(result.data)

@app.route("/tournaments/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    tourn = Tournament.query.get(tournament_id)
    result = tournament_schema.dump(tourn)
    return jsonify(result.data)
    
@app.route("/tournaments/update", methods=["GET"])
def tournaments_update():
    if current_user():
        try:
            coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)
            if not coach.web_admin:
                raise InvalidUsage("Coach does not have webadmin role", status_code=403)    
            TournamentService.update()
            return jsonify(True)
        except RegistrationError as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/tournaments/<int:tournament_id>/close", methods=["POST"])
def tournament_close(tournament_id):
    if current_user():
        try:
            tourn = Tournament.query.get(tournament_id)
            coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)    
            if not coach.web_admin:
                raise InvalidUsage("Coach does not have webadmin role", status_code=403)    
            #prizes
            for prize in request.get_json():
                tmp_coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).get(prize['coach'])
                reason = prize['reason']+" by "+coach.short_name()
                TransactionService.process(tmp_coach,int(prize['amount'])*-1,reason)

            for coach in tourn.coaches:
                TournamentService.unregister(tourn,coach,admin=True,refund=False)
            tourn.phase="deck_building"
            db.session.commit()

            result = tournament_schema.dump(tourn)
            return jsonify(result.data)
        except (RegistrationError,TransactionError) as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/tournaments/<int:tournament_id>/set_phase", methods=["POST"])
def tournament_set_phase(tournament_id):
    if current_user():
        try:
            tourn = Tournament.query.get(tournament_id)
            coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)    
            if not coach.short_name()==tourn.admin:
                raise InvalidUsage("You are not admin for this tournament!", status_code=403)    
            phase = request.get_json()['phase']
            if phase not in ["deck_building","locked","special_play","inducement"]:
                raise InvalidUsage(f"Incorrect phase - {phase}", status_code=403)  
            tourn.phase=phase
            db.session.commit()

            result = tournament_schema.dump(tourn)
            return jsonify(result.data)
        except (RegistrationError,TransactionError) as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/tournaments/<int:tournament_id>/sign", methods=["GET"])
def tournament_sign(tournament_id):
    if current_user():
        try:
            tourn = Tournament.query.get(tournament_id)
            coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)    
            TournamentService.register(tourn,coach)
            result = tournament_schema.dump(tourn)
            return jsonify(result.data)
        except RegistrationError as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/tournaments/<int:tournament_id>/resign", methods=["GET"])
def tournament_resign(tournament_id):
    if current_user():
        try:
            tourn = Tournament.query.get(tournament_id)
            coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)    
            
            TournamentService.unregister(tourn,coach)
            signups = TournamentService.update_signups(tourn)
            if len(signups)>0:
                coaches = [signup.coach for signup in signups]
                msg = (", ").join([f"<@{coach.disc_id}>" for coach in coaches])           
                NotificationService.notify(f"{msg}: Your signup to {tourn.name} has been updated from RESERVE to ACTIVE")

            result = tournament_schema.dump(tourn)
            return jsonify(result.data)
        except RegistrationError as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)


def dust_template(mode="add",card_id=None):
    if current_user():
        try:
            coach = Coach.query.filter_by(disc_id=current_user()['id']).one_or_none()
            if not coach:
                raise InvalidUsage("Coach not found", status_code=403)
            if mode=="add":
                DusterService.dust_card_by_id(coach,card_id)
            elif mode=="remove":
                DusterService.undust_card_by_id(coach,card_id)
            elif mode=="cancel":
               DusterService.cancel_duster(coach)
            elif mode=="commit":
                DusterService.commit_duster(coach)
            result = duster_schema.dump(coach.duster)
            return jsonify(result.data)
        except (DustingError,TransactionError) as e:
            raise InvalidUsage(str(e), status_code=403)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/duster/cancel", methods=["GET"])
def dust_cancel():
    return dust_template("cancel")

@app.route("/duster/commit", methods=["GET"])
def dust_commit():
    return dust_template("commit")

@app.route("/duster/add/<int:card_id>", methods=["GET"])
def card_dust_add(card_id):
    return dust_template("add",card_id)

@app.route("/duster/remove/<int:card_id>", methods=["GET"])
def card_dust_remove(card_id):
    return dust_template("remove",card_id)

@app.route("/coaches/<int:coach_id>", methods=["GET"])
def get_coach(coach_id):
    coach = Coach.query.get(coach_id)
    if coach is None:
        abort(404)
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@app.route("/coaches/<int:coach_id>", methods=["PUT"])
def update_coach(coach_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)
    
    tcoach = Coach.query.filter_by(disc_id=current_user()['id']).one_or_none()
    if not tcoach:
        raise InvalidUsage("Coach not found", status_code=403)
    if not tcoach.web_admin:
        raise InvalidUsage("Coach does not have webadmin role", status_code=403)    

    coach = Coach.query.get(coach_id)
    if coach is None:
        abort(404)

    bb2_name = request.get_json()['name']
    coach.bb2_name=bb2_name
    db.session.commit()
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@app.route("/cards/starter", methods=["GET"])
def get_starter_cards():
    starter_cards = PackService.generate("starter").cards
    result = cards_schema.dump(starter_cards)
    return jsonify(result.data)

# BB teams
@app.route("/teams/<teamname>", methods=["GET"])
def get_team(teamname):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)
    
    result = BB2Service.team(teamname)
    return jsonify(result)
# DECKS

def locked(deck):
    return True if deck.tournament_signup.tournament.phase=="locked" else False

@app.route("/decks/<int:deck_id>", methods=["GET"])
def get_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)

    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()

    if not deck.commited and not (coach.id==deck.tournament_signup.coach.id or coach.short_name()=="TomasT"):
        raise InvalidUsage("Deck not commited, only owner can display it!", status_code=403)

    # is committed    
    if deck.tournament_signup.tournament.phase=="deck_building" and not (coach.id==deck.tournament_signup.coach.id or coach.short_name()==deck.tournament_signup.tournament.admin or coach.short_name()=="TomasT"):
        raise InvalidUsage("Only owner and admin can see display commited deck in the Deck Building phase!", status_code=403)    

    starter_cards = CoachService.get_starter_cards(deck.tournament_signup.coach)
    result = deck_schema.dump(deck)
    result2 = cards_schema.dump(starter_cards)
    return jsonify({'deck':result.data, 'starter_cards':result2.data})

# updates just base deck info not cards
@app.route("/decks/<int:deck_id>", methods=["POST"])
def update_deck(deck_id):
    if current_user():
        deck = Deck.query.get(deck_id)
        if deck is None:
            abort(404)
        if locked(deck):
            raise InvalidUsage('Deck is locked!', status_code=403)

        coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
        if deck.tournament_signup.coach!=coach:
            raise InvalidUsage("Unauthorized access!", status_code=403)

        received_deck = request.get_json()['deck']
        deck = DeckService.update(deck,received_deck)
        result = deck_schema.dump(deck)
        return jsonify(result.data)
    else:
        raise InvalidUsage('You are not authenticated!', status_code=401)

# updates just base deck info not cards
@app.route("/decks/<int:deck_id>/addcard", methods=["POST"])
def addcard_deck(deck_id):
    if current_user():
        deck = Deck.query.get(deck_id)
        if deck is None:
            abort(404)
        if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

        coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
        if deck.tournament_signup.coach!=coach:
            raise InvalidUsage("Unauthorized access!", status_code=403)

        card = request.get_json()
        try:
            deck = DeckService.addcard(deck,card)
        except (DeckError) as e:
            raise InvalidUsage(str(e), status_code=403)

        result = deck_schema.dump(deck)
        return jsonify(result.data)
    else:
        raise InvalidUsage('You are not authenticated', status_code=401)

@app.route("/decks/<int:deck_id>/assign", methods=["POST"])
def assigncard_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)

    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
    if deck.tournament_signup.coach!=coach:
        raise InvalidUsage("Unauthorized access!", status_code=403)

    card = request.get_json()
    try:
        deck = DeckService.assigncard(deck,card)
    except (DeckError) as e:
        raise InvalidUsage(str(e), status_code=403)

    result = deck_schema.dump(deck)
    return jsonify(result.data)
    
@app.route("/decks/<int:deck_id>/addcard/extra", methods=["POST"])
def addcardextra_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)
    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
    if deck.tournament_signup.coach!=coach:
        raise InvalidUsage("Unauthorized access!", status_code=403)

    name = request.get_json()['name']
    try:
        deck = DeckService.addextracard(deck,name)
    except (DeckError) as e:            
        raise InvalidUsage(str(e), status_code=403)

    result = deck_schema.dump(deck)
    return jsonify(result.data)

@app.route("/decks/<int:deck_id>/removecard/extra", methods=["POST"])
def removecardextra_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)
    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
    if deck.tournament_signup.coach!=coach:
        raise InvalidUsage("Unauthorized access!", status_code=403)

    card = request.get_json()
    try:
        deck = DeckService.removeextracard(deck,card)
    except (DeckError) as e:            
        raise InvalidUsage(str(e), status_code=403)

    result = deck_schema.dump(deck)
    return jsonify(result.data)

@app.route("/decks/<int:deck_id>/remove", methods=["POST"])
def removecard_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)

    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
    if deck.tournament_signup.coach!=coach:
        raise InvalidUsage("Unauthorized access!", status_code=403)

    card = request.get_json()
    try:
        deck = DeckService.removecard(deck,card)
    except (DeckError) as e:
        raise InvalidUsage(str(e), status_code=403)

    result = deck_schema.dump(deck)
    return jsonify(result.data)
    
# commits deck
@app.route("/decks/<int:deck_id>/commit", methods=["GET"])
def commit_deck(deck_id):
    if not current_user():
        raise InvalidUsage('You are not authenticated', status_code=401)
    
    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if locked(deck):
            raise InvalidUsage("Deck is locked!", status_code=403)

    coach = Coach.query.options(raiseload(Coach.cards),raiseload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
    if deck.tournament_signup.coach!=coach:
        raise InvalidUsage("Unauthorized access!!!!", status_code=403)

    try:
        deck = DeckService.commit(deck)
    except (DeckError) as e:
        raise InvalidUsage(str(e), status_code=403)

    result = deck_schema.dump(deck)
    return jsonify(result.data)

# run the application
if __name__ == "__main__":
    app.run()
