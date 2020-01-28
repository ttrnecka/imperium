"""resets coaches and tournaments in DB"""
from sqlalchemy.orm.attributes import flag_modified
from web import db, app
from models.data_models import Coach, Tournament, TournamentSignups, Deck, achievements_template, deck_card_table
from services import CoachService

app.app_context().push()

for coach in Coach.query.all():
    coach.deleted = True
    coach.achievements = achievements_template

d = deck_card_table.delete()
db.session.execute(d)
TournamentSignups.query.delete()
Deck.query.delete()
Tournament.query.delete()

db.session.commit()
