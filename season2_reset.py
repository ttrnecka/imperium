"""resets coaches and tournaments in DB"""
from web import db, create_app
from models.data_models import Coach, Tournament, TournamentSignups
from services import CoachService

app = create_app()
app.app_context().push()

for coach in Coach.query.all():
    coach.deleted = True

TournamentSignups.query.delete()
Tournament.query.delete()

db.session.commit()
