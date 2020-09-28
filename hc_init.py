"""resets coaches and tournaments in DB"""
from web import db, create_app
from models.data_models import Coach, HighCommand

app = create_app()
app.app_context().push()


coaches = Coach.query.with_deleted().all()

for coach in coaches:
  if not coach.high_command:
    coach.high_command = HighCommand()

db.session.commit()
