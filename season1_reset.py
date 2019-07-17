"""resets coaches and tournaments in DB"""
from web import db, create_app
from models.data_models import Coach, Tournament
from services import CoachService

app = create_app()
app.app_context().push()

#for coach in Coach.query.with_deleted().all():
#    db.session.delete(coach)

#for tourn in Tournament.query.all():
#    db.session.delete(tourn)

for coach in Coach.query.all():
    CoachService.check_collect_three_legends_quest(coach)

db.session.commit()
