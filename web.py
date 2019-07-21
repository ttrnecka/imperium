"""web process"""
import os
import json
from datetime import timedelta

from flask import Flask, render_template, jsonify, abort, session, redirect, request, url_for
from flask_fontawesome import FontAwesome
from flask_migrate import Migrate
from sqlalchemy.orm import raiseload
from requests_oauthlib import OAuth2Session

from models.base_model import db
from models.data_models import Coach, Tournament
from models.data_models import TransactionError, Deck
from models.marsh_models import ma, coach_schema, cards_schema, coaches_schema
from models.marsh_models import tournaments_schema, tournament_schema, duster_schema
from models.marsh_models import leaderboard_coach_schema, deck_schema
from services import PackService, CoachService, NotificationService
from services import LedgerNotificationService, AchievementNotificationService
from services import AdminNotificationService
from services import TournamentService, RegistrationError
from services import BB2Service, DusterService, WebHook, DustingError
from services import TransactionService, DeckService, DeckError
from misc.helpers import InvalidUsage, current_coach
from misc.decorators import authenticated, registered, webadmin
import bb2


os.environ["YOURAPPLICATION_SETTINGS"] = "config/config.py"
ROOT = os.path.dirname(__file__)

def create_app():
    """return initialized flask app"""
    fapp = Flask(__name__)
    fapp.config["DEBUG"] = True
    fapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    fapp.config.from_envvar('YOURAPPLICATION_SETTINGS')
    db.init_app(fapp)
    ma.init_app(fapp)
    FontAwesome(fapp)

    # register wehook as Tournament service notifier
    NotificationService.register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_BANK']).send)
    LedgerNotificationService.register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_LEDGER']).send)
    AchievementNotificationService.register_notifier(
        WebHook(fapp.config['DISCORD_WEBHOOK_ACHIEVEMENTS']).send
    )
    AdminNotificationService.register_notifier(
        WebHook(fapp.config['DISCORD_WEBHOOK_ADMIN']).send
    )
    BB2Service.register_agent(bb2.api.Agent(fapp.config['BB2_API_KEY']))
    return fapp

app = create_app()
migrate = Migrate(app, db)

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

STORE = os.path.join(ROOT, 'data', f"season{app.config['SEASON']}")
STATS_FILE = os.path.join(STORE, "stats.json")

def get_stats(fresh=False):
    """pulls data from stats file"""
    if not fresh and os.path.isfile(STATS_FILE):
        file = open(STATS_FILE, "r")
        data = json.loads(file.read())
        file.close()
        return data
    else:
        return {
            'coaches': {},
            'teams': {},
            'matchfiles':[]
        }

if 'http://' in app.config["OAUTH2_REDIRECT_URI"]:
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

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Error handler"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/signin')
def signin():
    """sign using discord OAUTH"""
    scope = request.args.get(
        'scope',
        'identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
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
    # STORE it in session
    session['discord_user'] = user
    return redirect(url_for('.index'))

@app.before_request
def before_request():
    """set session to last 30 days"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route('/me')
def me():
    """returns user from session"""
    return jsonify(user=session.get('discord_user', {'code':0}))

@app.route("/")
def index():
    """render index"""
    bb2_names = sorted(list(get_stats()['coaches'].keys()))
    return render_template("index.html", bb2_names=bb2_names)

@app.route("/coaches", methods=["GET"])
def get_coaches():
    """returns all coaches as json"""
    all_coaches = Coach.query.options(raiseload(Coach.cards), raiseload(Coach.packs)).all()
    result = coaches_schema.dump(all_coaches)
    return jsonify(result.data)

@app.route("/coaches/leaderboard", methods=["GET"])
def get_coaches_leaderboard():
    """return leaderboard json"""
    all_coaches = Coach.query.all()
    result = {}
    result['coaches'] = leaderboard_coach_schema.dump(all_coaches).data
    result['coach_stats'] = list(get_stats()['coaches'].values())
    return jsonify(result)

@app.route("/tournaments", methods=["GET"])
def get_tournaments():
    """returns all tournaments as json"""
    all_tournaments = Tournament.query.options(
        raiseload(Tournament.coaches)
    ).filter(Tournament.status.in_(("OPEN", "RUNNING"))).all()

    result = tournaments_schema.dump(all_tournaments)
    return jsonify(result.data)

@app.route("/tournaments/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    """returns tournamnet as json"""
    tourn = Tournament.query.get(tournament_id)
    result = tournament_schema.dump(tourn)
    return jsonify(result.data)

@app.route("/tournaments/update", methods=["GET"])
@authenticated
@webadmin
def tournaments_update():
    """Update tournaments from sheet"""
    try:
        TournamentService.update()
        return jsonify(True)
    except RegistrationError as exc:
        raise InvalidUsage(str(exc), status_code=403)

@app.route("/tournaments/<int:tournament_id>/close", methods=["POST"])
@authenticated
@webadmin
def tournament_close(tournament_id):
    """Close tournaments and award prizes"""
    try:
        tourn = Tournament.query.get(tournament_id)
        coach = current_coach()
        #prizes
        for prize in request.get_json():
            tmp_coach = Coach.query.options(
                raiseload(Coach.cards), raiseload(Coach.packs)
            ).get(prize['coach'])

            reason = prize['reason']+" by "+coach.short_name()
            TransactionService.process(tmp_coach, int(prize['amount'])*-1, reason)

        for coach in tourn.coaches:
            TournamentService.unregister(tourn, coach, admin=True, refund=False)
        TournamentService.reset_phase(tourn)
        db.session.commit()

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except (RegistrationError, TransactionError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

@app.route("/tournaments/<int:tournament_id>/set_phase", methods=["POST"])
@authenticated
@webadmin
def tournament_set_phase(tournament_id):
    """Set tournament phase"""
    try:
        tourn = Tournament.query.get(tournament_id)
        phase = request.get_json()['phase']
        TournamentService.set_phase(tourn, phase)
        db.session.commit()

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except (RegistrationError, TransactionError, TypeError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

@app.route("/tournaments/<int:tournament_id>/sign", methods=["GET"])
@authenticated
@registered
def tournament_sign(tournament_id, **kwargs):
    """Sign coach into tournament"""
    try:
        coach = kwargs['coach']

        tourn = Tournament.query.get(tournament_id)
        TournamentService.register(tourn, coach)
        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except RegistrationError as exc:
        raise InvalidUsage(str(exc), status_code=403)

@app.route("/tournaments/<int:tournament_id>/resign", methods=["GET"])
@authenticated
@registered
def tournament_resign(tournament_id, **kwargs):
    """resign from tournament"""
    try:
        coach = kwargs['coach']

        tourn = Tournament.query.get(tournament_id)
        TournamentService.unregister(tourn, coach)
        signups = TournamentService.update_signups(tourn)
        if signups:
            coaches = [signup.coach for signup in signups]
            msg = (", ").join([f"<@{coach.disc_id}>" for coach in coaches])
            NotificationService.notify(
                f"{msg}: Your signup to {tourn.name} has been updated from RESERVE to ACTIVE"
            )

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except RegistrationError as exc:
        raise InvalidUsage(str(exc), status_code=403)

@authenticated
@registered
def dust_template(mode="add", card_id=None, **kwargs):
    """wrapper around various dust calls"""
    try:
        coach = kwargs['coach']
        if mode == "add":
            DusterService.dust_card_by_id(coach, card_id)
        elif mode == "remove":
            DusterService.undust_card_by_id(coach, card_id)
        elif mode == "cancel":
            DusterService.cancel_duster(coach)
        elif mode == "commit":
            DusterService.commit_duster(coach)
        result = duster_schema.dump(coach.duster)
        return jsonify(result.data)
    except (DustingError, TransactionError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

@app.route("/duster/cancel", methods=["GET"])
def dust_cancel():
    """cancels dusting"""
    return dust_template("cancel")

@app.route("/duster/commit", methods=["GET"])
def dust_commit():
    """commits dusting"""
    return dust_template("commit")

@app.route("/duster/add/<int:card_id>", methods=["GET"])
def card_dust_add(card_id):
    """adds card to dusting"""
    return dust_template("add", card_id)

@app.route("/duster/remove/<int:card_id>", methods=["GET"])
def card_dust_remove(card_id):
    """removes card from dusting"""
    return dust_template("remove", card_id)

@app.route("/coaches/<int:coach_id>", methods=["GET"])
def get_coach(coach_id):
    """get coach with detailed info"""
    coach = Coach.query.get(coach_id)
    if coach is None:
        abort(404)
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@app.route("/coaches/<int:coach_id>", methods=["PUT"])
@authenticated
@webadmin
def update_coach(coach_id):
    """Update coaches bb2 name"""
    coach = Coach.query.get(coach_id)
    if coach is None:
        abort(404)

    bb2_name = request.get_json()['name']
    coach.bb2_name = bb2_name
    db.session.commit()
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@app.route("/cards/starter", methods=["GET"])
def get_starter_cards():
    """loads starter cards as json"""
    starter_cards = PackService.generate("starter").cards
    result = cards_schema.dump(starter_cards)
    return jsonify(result.data)

# BB teams
@app.route("/teams/<teamname>", methods=["GET"])
@authenticated
def get_team(teamname):
    """pulls team from BB2 api and returns it"""
    result = BB2Service.team(teamname)
    return jsonify(result)
# DECKS

def locked(deck):
    """check if tournament the deck is in is locked"""
    return deck.tournament_signup.tournament.phase in ["locked", "blood_bowl"]

def get_deck_or_abort(deck_id):
    """Returns deck or aborts"""
    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    return deck

def get_unlocked_deck_or_abort(deck_id):
    """Returns InvalidUsage if the deck is locked, otherwise returns deck if it exits"""
    deck = get_deck_or_abort(deck_id)
    if locked(deck):
        raise InvalidUsage("Deck is locked!", status_code=403)
    return deck

def can_edit_deck(deck):
    """Checks if deck belongs to the current coach, otherwise raises InvalidUsage"""
    if deck.tournament_signup.coach != current_coach():
        raise InvalidUsage("Unauthorized access!!!!", status_code=403)
    return True

def deck_response(deck):
    """Turns deck into JSON response"""
    result = deck_schema.dump(deck)
    return jsonify(result.data)

@app.route("/decks/<int:deck_id>", methods=["GET"])
@authenticated
def get_deck(deck_id):
    """loads deck"""
    deck = get_deck_or_abort(deck_id)
    coach = current_coach()

    if (not deck.commited and
            not (coach.id == deck.tournament_signup.coach.id or coach.short_name() == "TomasT")):
        raise InvalidUsage("Deck not commited, only owner can display it!", status_code=403)

    # is committed
    if (deck.tournament_signup.tournament.phase == "deck_building" and
            not (coach.id == deck.tournament_signup.coach.id or
                 coach.short_name() == deck.tournament_signup.tournament.admin or
                 coach.short_name() == "TomasT")
       ):
        raise InvalidUsage(
            "Only owner and admin can see display commited deck in the Deck Building phase!",
            status_code=403
        )

    starter_cards = CoachService.get_starter_cards(deck.tournament_signup.coach)
    result = deck_schema.dump(deck)
    result2 = cards_schema.dump(starter_cards)
    return jsonify({'deck':result.data, 'starter_cards':result2.data})

@app.route("/decks/<int:deck_id>", methods=["POST"])
@authenticated
def update_deck(deck_id):
    """Updates base deck info not cards"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    received_deck = request.get_json()['deck']
    deck = DeckService.update(deck, received_deck)
    return deck_response(deck)

# updates just base deck info not cards
@app.route("/decks/<int:deck_id>/addcard", methods=["POST"])
@authenticated
def addcard_deck(deck_id):
    """Adds cards to deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.addcard(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@app.route("/decks/<int:deck_id>/assign", methods=["POST"])
@authenticated
def assigncard_deck(deck_id):
    """Assigns card in deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.assigncard(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@app.route("/decks/<int:deck_id>/addcard/extra", methods=["POST"])
@authenticated
def addcardextra_deck(deck_id):
    """Adds extra card to deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    name = request.get_json()['name']
    try:
        deck = DeckService.addextracard(deck, name)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@app.route("/decks/<int:deck_id>/removecard/extra", methods=["POST"])
@authenticated
def removecardextra_deck(deck_id):
    """Removes extra card from deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.removeextracard(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@app.route("/decks/<int:deck_id>/remove", methods=["POST"])
@authenticated
def removecard_deck(deck_id):
    """Removes cards from deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.removecard(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

# commits deck
@app.route("/decks/<int:deck_id>/commit", methods=["GET"])
@authenticated
def commit_deck(deck_id):
    """Commits deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    try:
        deck = DeckService.commit(deck)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

# run the application
if __name__ == "__main__":
    app.run()
