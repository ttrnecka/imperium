# Works with Python 3.6
import os

from web import db, app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups, Deck
from sqlalchemy.orm.attributes import flag_modified


app.app_context().push()

ROOT = os.path.dirname(__file__)

for card in Card.query.all():
        card.assigned_to_array={}
for deck in Deck.query.all():
        for card in deck.extra_cards:
                card['assigned_to_array']={}
        for card in deck.unused_extra_cards:
                card['assigned_to_array']={}
        for card in deck.starter_cards:
                card['assigned_to_array']={}

        flag_modified(deck, "extra_cards")
        flag_modified(deck, "unused_extra_cards")
        flag_modified(deck, "starter_cards")
db.session.commit()