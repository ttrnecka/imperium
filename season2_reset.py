"""resets coaches and tournaments in DB"""
from sqlalchemy.orm.attributes import flag_modified
from web import db, create_app
from models.data_models import Coach, Tournament, TournamentSignups, Deck, achievements_template
from services import CoachService

app = create_app()
app.app_context().push()

for coach in Coach.query.all():
    coach.deleted = True
    coach.achievements = achievements_template

TournamentSignups.query.delete()
Deck.query.delete()
Tournament.query.delete()

db.session.commit()
