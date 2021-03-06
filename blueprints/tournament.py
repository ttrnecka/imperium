import itertools, os, json
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import raiseload

from models.data_models import db, Tournament, Coach, TransactionError
from models.marsh_models import tournaments_schema, tournament_schema
from misc.decorators import authenticated, webadmin, registered, superadmin
from misc.helpers import InvalidUsage, current_coach
from misc.stats import StatsHandler
import bb2_cyanide_api as bb2

from services import TournamentService, RegistrationError, TransactionService, TournamentError
from services import Notificator
from misc.helpers2 import etagjsonify

tournament = Blueprint('tournaments', __name__)

@tournament.route("", methods=["GET"])
def get_tournaments():
    """returns all tournaments as json"""
    all_tournaments = Tournament.query.options(
        raiseload(Tournament.coaches)
    ).filter(Tournament.status.in_(("OPEN", "RUNNING"))).all()

    result = tournaments_schema.dump(all_tournaments)
    return etagjsonify(result.data)

@tournament.route("/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    """returns tournamnet as json"""
    tourn = Tournament.query.get(tournament_id)
    result = tournament_schema.dump(tourn)
    return jsonify(result.data)

@tournament.route("/<int:tournament_id>/leaderboard", methods=["GET"])
def get_tournament_leaderboard(tournament_id):
    """returns tournamnet as json"""
    tourn = Tournament.query.get(tournament_id)
    matches = []
    st = StatsHandler()
    for comp in tourn.competitions:
      folder = st.competition_folder(comp.comp_id)
      if os.path.isdir(folder):
        matchfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

        for file_name in matchfiles:
          file = open(os.path.join(folder, file_name), "r")
          data = json.loads(file.read())
          file.close()
          matches.append(bb2.Match(data))
    t = bb2.Tournament(*matches)
    
    return jsonify(t.leaderboard())

@tournament.route("/<int:tournament_id>/cards", methods=["GET"])
@authenticated
@webadmin
def tournaments_cards(tournament_id):
    """Update tournaments from sheet"""
    tourn = Tournament.query.get(tournament_id)
    return jsonify(TournamentService.cards(tourn))


@tournament.route("/update", methods=["GET"])
@authenticated
@superadmin
def tournaments_update():
    """Update tournaments from sheet"""
    try:
        TournamentService.update()
        all_tournaments = Tournament.query.options(
            raiseload(Tournament.coaches)
        ).filter(Tournament.status.in_(("OPEN", "RUNNING"))).all()

        result = tournaments_schema.dump(all_tournaments)
        return jsonify(result.data)
    except RegistrationError as exc:
        raise InvalidUsage(str(exc), status_code=403)

@tournament.route("/<int:tournament_id>/close", methods=["POST"])
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

        TournamentService.close_tournament(tourn)

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except (RegistrationError, TransactionError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

@tournament.route("/<int:tournament_id>/set_phase", methods=["POST"])
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

@tournament.route("/<int:tournament_id>/start", methods=["GET"])
@authenticated
@superadmin
def tournament_start(tournament_id):
    """Set tournament phase"""
    try:
        tourn = Tournament.query.get(tournament_id)
        TournamentService.kick_off(tourn)

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except (RegistrationError, TransactionError, TypeError, TournamentError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

@tournament.route("/<int:tournament_id>/sign", methods=["GET"])
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

@tournament.route("/<int:tournament_id>/resign", methods=["GET"])
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
            Notificator("bank").notify(
                f"{msg}: Your signup to {tourn.name} has been updated from RESERVE to ACTIVE"
            )

        result = tournament_schema.dump(tourn)
        return jsonify(result.data)
    except RegistrationError as exc:
        raise InvalidUsage(str(exc), status_code=403)
