from flask import Blueprint, jsonify

from models.data_models import TransactionError
from models.marsh_models import duster_schema
from misc.decorators import authenticated, registered
from misc.helpers import InvalidUsage

from services import DusterService, DustingError

duster = Blueprint('duster', __name__)

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

@duster.route("/cancel", methods=["GET"])
def dust_cancel():
    """cancels dusting"""
    return dust_template("cancel")

@duster.route("/commit", methods=["GET"])
def dust_commit():
    """commits dusting"""
    return dust_template("commit")

@duster.route("/add/<int:card_id>", methods=["GET"])
def card_dust_add(card_id):
    """adds card to dusting"""
    return dust_template("add", card_id)

@duster.route("/remove/<int:card_id>", methods=["GET"])
def card_dust_remove(card_id):
    """removes card from dusting"""
    return dust_template("remove", card_id)
