# Works with Python 3.6
import os

from web import db, app
from models.data_models import Coach, Account, Card, Pack, Transaction, TransactionError, Tournament, TournamentSignups, Deck


app.app_context().push()

ROOT = os.path.dirname(__file__)

for ts in TournamentSignups.query.all():
    ts.deck.skill_allocations = Deck(team_name="",mixed_team="", tournament_signup = ts, extra_cards = [], unused_extra_cards = [], starter_cards = [])
    db.session.add(deck)
    db.session.commit()