# Works with Python 3.6
import os

from web import db, app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups, Deck
from sqlalchemy.orm.attributes import flag_modified


app.app_context().push()

ROOT = os.path.dirname(__file__)

for t in Tournament.query.all():
    if t.phase=="":
        t.phase="deck_building"
        db.session.commit()

for ts in TournamentSignups.query.all():
    if not ts.deck:
        deck = Deck(team_name="",mixed_team="", tournament_signup = ts, extra_cards = [], unused_extra_cards = [], starter_cards = [])
        db.session.add(deck)
        db.session.commit()