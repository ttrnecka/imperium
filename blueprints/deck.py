from flask import Blueprint, jsonify, abort, request

from models.data_models import db, Tournament, Deck
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
@authenticated
def update_deck(deck_id):
    """Updates base deck info not cards"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    received_deck = request.get_json()['deck']
    deck = DeckService.update(deck, received_deck)
    return deck_response(deck)

# updates just base deck info not cards
@deck.route("/<int:deck_id>/addcard", methods=["POST"])
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

@deck.route("/<int:deck_id>/assign", methods=["POST"])
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

@deck.route("/<int:deck_id>/disable", methods=["POST"])
@authenticated
def disablecard_deck(deck_id):
    """Assigns card in deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.disable_card(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@deck.route("/<int:deck_id>/enable", methods=["POST"])
@authenticated
def enablecard_deck(deck_id):
    """Assigns card in deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    card = request.get_json()
    try:
        deck = DeckService.enable_card(deck, card)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)

@deck.route("/<int:deck_id>/addcard/extra", methods=["POST"])
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

@deck.route("/<int:deck_id>/removecard/extra", methods=["POST"])
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

@deck.route("/<int:deck_id>/remove", methods=["POST"])
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

@deck.route("/<int:deck_id>/commit", methods=["GET"])
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

@deck.route("/<int:deck_id>/reset", methods=["GET"])
@authenticated
def reset_deck(deck_id):
    """Resets deck"""
    deck = get_unlocked_deck_or_abort(deck_id)
    can_edit_deck(deck)

    try:
        deck = DeckService.reset(deck)
    except (DeckError) as exc:
        raise InvalidUsage(str(exc), status_code=403)

    return deck_response(deck)
