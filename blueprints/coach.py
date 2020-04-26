from flask import Blueprint, jsonify, abort, request
from sqlalchemy.orm import raiseload, selectinload

from models.data_models import db, Coach, TransactionError
from models.marsh_models import coach_schema, coaches_schema, cards_schema
from misc.decorators import authenticated, registered_with_inactive, webadmin
from misc.helpers import InvalidUsage, current_user, owning_coach, CardHelper

from services import CoachService
from misc.stats import StatsHandler
from misc.helpers2 import current_season, etagjsonify, cache_header

coach = Blueprint('coaches', __name__)

@coach.route('', methods=["GET"])
@cache_header(300)
def get_coaches():
    """returns all coaches as json"""
    all_coaches = Coach.query.options(raiseload(Coach.cards), raiseload(Coach.packs)).all()
    result = coaches_schema.dump(all_coaches)
    return etagjsonify(result.data)


@authenticated
@coach.route("", methods=["POST"])
def new_coach():
    """creates new coach"""
    try:
        user = current_user()
        name = user['username']+"#"+user['discriminator']
        coach = CoachService.new_coach(name,user['id'])
    except TransactionError as exc:
        raise InvalidUsage(str(exc), status_code=403)

    result = coach_schema.dump(coach)
    return jsonify(result.data)

@coach.route("/leaderboard", methods=["GET"])
@cache_header(300)
def get_coaches_leaderboard():
    """return leaderboard json"""
    season = request.args.get("season", current_season())
    stats = StatsHandler(season)
    result = {}
    result['coaches'] = stats.get_stats()['coaches_extra']
    result['coach_stats'] = list(stats.get_stats()['coaches'].values())
    return etagjsonify(result)

@coach.route("/<int:coach_id>", methods=["GET"])
def get_coach(coach_id):
    """get coach with detailed info"""
    coach = Coach.query.options(selectinload(Coach.packs)).get(coach_id)
    if coach is None:
        abort(404)
    result = coach_schema.dump(coach)
    if not owning_coach(coach):
        CardHelper.censor_cards(result.data['cards'])
    return etagjsonify(result.data)

@coach.route("/<int:coach_id>/stats", methods=["GET"])
@cache_header(300)
def get_coach_stats(coach_id):
    """get coach with detailed info"""
    coach = Coach.query.options(selectinload(Coach.packs)).get(coach_id)
    season = request.args.get("season", current_season())
    if coach is None:
        abort(404)
    return etagjsonify(coach.stats(season))

@coach.route("/<int:coach_id>/activate", methods=["PUT"])
@authenticated
@registered_with_inactive
def activate_coach(coach_id, **kwargs):
    """Activates coach"""
    coach = kwargs['coach']
    if coach is None:
        abort(404)
    if not owning_coach(coach):
        raise InvalidUsage("Unauthorized access!!!!", status_code=403)
    try:
        card_ids = request.get_json()['card_ids']
        CoachService.activate_coach(coach=coach,card_ids=card_ids)
    except (ValueError,TypeError,TransactionError) as exc:
        raise InvalidUsage(str(exc), status_code=403)
    result = coach_schema.dump(coach)
    return jsonify(result.data)

@coach.route("/<int:coach_id>/cards/inactive", methods=["GET"])
@authenticated
@registered_with_inactive
def inactive_coach_cards(coach_id, **kwargs):
    """Activates coach"""
    coach = kwargs['coach']
    if coach is None:
        abort(404)
    result = cards_schema.dump(coach.inactive_cards())
    return jsonify(result.data)

@coach.route("/<int:coach_id>", methods=["PUT"])
@authenticated
@webadmin
def update_coach(coach_id):
    """Update coaches bb2 name"""
    coach = Coach.query.options(selectinload(Coach.packs)).get(coach_id)
    if coach is None:
        abort(404)

    bb2_name = request.get_json()['name']
    coach.bb2_name = bb2_name
    db.session.commit()
    result = coach_schema.dump(coach)
    return jsonify(result.data)