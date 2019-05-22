# Works with Python 3.6
import os

from web import db, app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups, Deck
from sqlalchemy.orm.attributes import flag_modified


app.app_context().push()

ROOT = os.path.dirname(__file__)

#for t in Tournament.query.all():
#    if t.phase=="":
#        t.phase="deck_building"
#        db.session.commit()

for card in Card.query.all():
        card.assigned_to_array = []
        db.session.commit()