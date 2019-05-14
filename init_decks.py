# Works with Python 3.6
import os

from web import db, app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups, Deck
from sqlalchemy.orm.attributes import flag_modified


app.app_context().push()

ROOT = os.path.dirname(__file__)

for ts in TournamentSignups.query.all():
    ts.deck.starter_cards=[]
    flag_modified(ts.deck, "starter_cards")
    db.session.commit()