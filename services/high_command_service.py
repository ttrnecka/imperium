"""DusterService helpers"""

from models.data_models import Coach, Transaction, Tournament, Card, CardTemplate
from models.base_model import db
from .notification_service import Notificator
from sqlalchemy.orm.attributes import flag_modified

class HighCommandError(Exception):
    """Exception used for High Commands Errors"""

class HighCommandSquadError(HighCommandError):
    """Exception used for High Commands Errors"""

MAX_LEVEL_ERROR = "Max High Command level reached!"
CANNOT_EDIT_ERROR = "Cannot edit High Command Squad in this phase!"
INVALID_CARD_ERROR = "Invalid action!"
SQUAD_FULL_ERROR = "High Command Squad is full!"
CARD_NOT_FOUND = "Card {} not found in the High Command Squad!"
BANNED_CARD = "Card is banned in the tournament!"
ALREADY_IN_SQUAD = "Card is already in High Command Squad!"

HC_PRICES = [
  10,20,30,40,50,60
]

def level(coach):
    """Level high command"""
    hc = coach.high_command

    # check if max level
    if len(HC_PRICES) == hc.level - 1:
      raise HighCommandError(MAX_LEVEL_ERROR)
    
    hc.level += 1
    reason = f"Updated High Command to level {hc.level}"
    tran = Transaction(description=reason, price=HC_PRICES[hc.level-2])
    coach.make_transaction(tran)
    Notificator("bank").notify(
        f"{coach.short_name()}: {reason}"
    )
    return True

def can_edit_squad(squad):
  if squad.deck.tournament_signup.tournament.phase != Tournament.DB_PHASE:
    raise HighCommandSquadError(CANNOT_EDIT_ERROR)

def valid_hc_card(card):
  if not isinstance(card, Card) \
      or card.get('card_type') != CardTemplate.TYPE_HC:
    raise HighCommandSquadError(INVALID_CARD_ERROR)

def add_card_to_squad(squad, card):
  can_edit_squad(squad)
  valid_hc_card(card)

  # check if squad has free slot
  if squad.level == squad.cards.count():
     raise HighCommandSquadError(SQUAD_FULL_ERROR)

  # checl if card is already there
  if card in squad.cards:
    raise HighCommandSquadError(ALREADY_IN_SQUAD)
  # add the card to squad
  squad.cards.append(card)
  card.assigned_to_array[squad.deck.id] = []
  flag_modified(card, "assigned_to_array")

  # increase card usage
  card.increment_use()
  db.session.commit()

def remove_card_from_squad(squad, card):
  can_edit_squad(squad)
  valid_hc_card(card)

  # check if card is in squad
  if card not in squad.cards:
    raise HighCommandSquadError(CARD_NOT_FOUND.format(card.template.name))

  squad.cards.remove(card)
  card.assigned_to_array[squad.deck.id] = []
  flag_modified(card, "assigned_to_array")
  # revert usage
  card.decrement_use()
  db.session.commit()

