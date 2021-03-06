"""web process"""
import os
from datetime import timedelta
from copy import deepcopy

from flask import Flask, render_template, session, request, jsonify
from blueprints import auth, coach, tournament, duster, deck, cracker
from flask_fontawesome import FontAwesome
from flask_migrate import Migrate
from sqlalchemy.orm import selectinload
from flask_admin import Admin
from flask_compress import Compress

from models.base_model import db
from models.data_models import Coach, Tournament
from models.marsh_models import ma, coach_schema
from services import Notificator
from services import BB2Service, WebHook
from services.high_command_service import HC_PRICES
from misc.stats import StatsHandler
from misc.helpers import InvalidUsage, current_user
from misc.decorators import authenticated
from misc.admin import TournamentView, CoachView
from misc.helpers2 import etagjsonify, cache, cache_header
import bb2_cyanide_api as bb2

os.environ["YOURAPPLICATION_SETTINGS"] = "config/config.py"

compress = Compress()

def create_app():
    """return initialized flask app"""
    fapp = Flask(__name__)
    fapp.config["DEBUG"] = True
    fapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    fapp.config.from_envvar('YOURAPPLICATION_SETTINGS')
    db.init_app(fapp)
    ma.init_app(fapp)
    compress.init_app(fapp)
    FontAwesome(fapp)
    fapp.register_blueprint(auth.auth)
    fapp.register_blueprint(coach.coach, url_prefix='/coaches')
    fapp.register_blueprint(tournament.tournament, url_prefix='/tournaments')
    fapp.register_blueprint(duster.duster, url_prefix='/duster')
    fapp.register_blueprint(deck.deck, url_prefix='/decks')
    fapp.register_blueprint(cracker.cracker, url_prefix='/api/cracker')


    admin = Admin(fapp, name='Management', template_mode='bootstrap3')
    # Add administrative views here
    admin.add_view(CoachView(Coach, db.session))
    admin.add_view(TournamentView(Tournament, db.session))
    # register wehook as Tournament service notifier
    Notificator("bank").register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_BANK']).send)
    Notificator("ledger").register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_LEDGER']).send)
    Notificator("achievement").register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_ACHIEVEMENTS']).send)
    Notificator("admin").register_notifier(
        WebHook(fapp.config['DISCORD_WEBHOOK_ADMIN']).send
    )
    Notificator('tournament').register_notifier(WebHook(fapp.config['DISCORD_WEBHOOK_TOURNAMENT']).send)
    BB2Service.register_agent(bb2.Agent(fapp.config['BB2_API_KEY']))
    return fapp

app = create_app()
migrate = Migrate(app, db)
cache.init_app(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Error handler"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
    
@app.before_request
def before_request():
    """set session to last 30 days"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

@app.route("/")
def index():
    """render index"""
    return render_template("index.html")

@app.route('/me')
def me():
    """returns user from session"""
    user = session.get('discord_user', {'code':0})
    if current_user():
        coach = Coach.query.with_deleted().options(selectinload(Coach.packs)).filter_by(disc_id=current_user()['id']).one_or_none()
        result = coach_schema.dump(coach)
        coach_data = result.data
    else:
        coach_data = {}
    cuser = deepcopy(user)
    cuser['coach'] = coach_data
    return jsonify(user=cuser)

@app.route("/bb2_names")
@cache_header(3600)
def bb2_names():
    """return  bb2_names"""
    bb2_names = sorted(list(StatsHandler().get_stats()['coaches'].keys()))
    return etagjsonify(names=bb2_names)
    
@app.route("/config")
@cache_header(3600)
def seasons():
    """return  config"""
    return etagjsonify(seasons=app.config['SEASONS'], high_command_prices = HC_PRICES)

# BB teams
@app.route("/teams/<teamname>", methods=["GET"])
@authenticated
def get_team(teamname):
    """pulls team from BB2 api and returns it"""
    result = BB2Service.team(teamname)
    return jsonify(result)
    
# run the application
if __name__ == "__main__":
    app.run()
