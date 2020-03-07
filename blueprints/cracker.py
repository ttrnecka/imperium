from flask import Blueprint, jsonify, request

from models.data_models import db
from models.marsh_models import cracker_cards_schema
from misc.decorators import cracker_api_user
from misc.helpers import InvalidUsage, represents_int

from services import CrackerService, InvalidCrackerType, InvalidCrackerTeam

cracker = Blueprint('cracker', __name__)

@cracker.route("/cards/<coach>", methods=["POST"])
@cracker_api_user
def generate_pack(coach):
    data = request.get_json()

    if 'pack_type' not in data.keys():
        raise InvalidUsage("Missing 'pack_type' argument!", status_code=403)
    if 'team' not in data.keys():
        raise InvalidUsage("Missing 'team' argument!", status_code=403)

    try:
        with db.session.no_autoflush:
            team = CrackerService.cracker_team(coach)
            db.session.add(team)
            db.session.commit()

            cards = CrackerService.generate_pack(data['pack_type'],data['team'])
            for card in cards:
                db.session.add(card)
                card.team_id = team.id
        db.session.commit()
        result = cracker_cards_schema.dump(cards)
    except (InvalidCrackerTeam,InvalidCrackerType) as exc:
        raise InvalidUsage(str(exc), status_code=403)
    return jsonify(result.data)


@cracker.route("/cards/<coach>", methods=["GET"])
@cracker_api_user
def cracker_coach_cards(coach):
    history = request.args.get('history')

    if history and represents_int(history):
        cards = CrackerService.history_cards(coach,int(history))
    else:
        cards = CrackerService.active_cards(coach)
    result = cracker_cards_schema.dump(cards)
    return jsonify(result.data)

@cracker.route("/cards/<coach>", methods=["DELETE"])
@cracker_api_user
def cracker_coach_deactivate_team(coach):
    team = CrackerService.cracker_team(coach)
    if team.id:
        team.active = False
        db.session.commit()
    return jsonify("OK")

@cracker.route("/cards", methods=["GET"])
@cracker_api_user
def cracker_cards():
    cards = CrackerService.active_cards()
    result = cracker_cards_schema.dump(cards)
    return jsonify(result.data)
