from flask import Blueprint, jsonify, abort, request

import functools

from models.data_models import db, Tournament, Deck, CardError
from models.marsh_models import deck_schema
from misc.decorators import authenticated
from misc.helpers import InvalidUsage, current_coach

from services import DeckService, DeckError

deck = Blueprint('decks', __name__)

def locked(deck):
    """check if tournament the deck is in is locked""" 
    return deck.tournament_signup.tournament.phase in [Tournament.LOCKED_PHASE, Tournament.BB_PHASE]

def get_deck_or_abort(deck_id):
    """Returns deck or aborts"""
    deck = db.session.query(Deck).with_for_update().get(deck_id)
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

def deck_response_deco(func):
    """Standard deck response"""
    @functools.wraps(func)
    @authenticated
    def wrapper_deck_response(deck_id):
        deck = get_unlocked_deck_or_abort(deck_id)
        can_edit_deck(deck)
        try:
          deck = func(deck)
        except (DeckError, CardError) as exc:
          raise InvalidUsage(str(exc), status_code=403)
        return deck_response(deck)
    return wrapper_deck_response

@deck.route("/<int:deck_id>", methods=["GET"])
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

    # any other phase only tournament admin or tournament signees can see it
    coach_ids = [ts.coach_id for ts in deck.tournament_signup.tournament.tournament_signups]
    if (coach.id not in coach_ids and
            not (coach.short_name() == deck.tournament_signup.tournament.admin or
                 coach.short_name() == "TomasT")
       ):
        raise InvalidUsage(
            "Only tournament participants or admin can display the decks!",
            status_code=403
        )
    return deck_response(deck)

@deck.route("/<int:deck_id>", methods=["POST"])
@deck_response_deco
def update_deck(deck):
    """Updates base deck info not cards"""
    return DeckService.update(deck, request.get_json()['deck'])

@deck.route("/<int:deck_id>/addcard", methods=["POST"])
@deck_response_deco
def addcard_deck(deck):
    """Adds cards to deck"""
    return DeckService.addcard(deck, request.get_json())

@deck.route("/<int:deck_id>/assign", methods=["POST"])
@deck_response_deco
def assigncard_deck(deck):
    """Assigns card in deck"""
    return DeckService.assigncard(deck, request.get_json())

@deck.route("/<int:deck_id>/disable", methods=["POST"])
@deck_response_deco
def disablecard_deck(deck):
    """Assigns card in deck"""
    return DeckService.disable_card(deck, request.get_json())

@deck.route("/<int:deck_id>/enable", methods=["POST"])
@deck_response_deco
def enablecard_deck(deck):
    """Assigns card in deck"""
    return DeckService.enable_card(deck, request.get_json())

@deck.route("/<int:deck_id>/addcard/extra", methods=["POST"])
@deck_response_deco
def addcardextra_deck(deck):
    """Adds extra card to deck"""
    return DeckService.addextracard(deck, request.get_json()['name'])

@deck.route("/<int:deck_id>/removecard/extra", methods=["POST"])
@deck_response_deco
def removecardextra_deck(deck):
    """Removes extra card from deck"""
    return DeckService.removeextracard(deck, request.get_json())

@deck.route("/<int:deck_id>/remove", methods=["POST"])
@deck_response_deco
def removecard_deck(deck):
    """Removes cards from deck"""
    return DeckService.removecard(deck, request.get_json())

@deck.route("/<int:deck_id>/commit", methods=["GET"])
@deck_response_deco
def commit_deck(deck):
    """Commits deck"""
    return DeckService.commit(deck)

@deck.route("/<int:deck_id>/reset", methods=["GET"])
@deck_response_deco
def reset_deck(deck):
    """Resets deck"""
    return DeckService.reset(deck)
