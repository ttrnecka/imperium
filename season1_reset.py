"""resets coaches and tournaments in DB"""
from web import db, create_app
from models.data_models import Coach, Tournament

app = create_app()
app.app_context().push()

for coach in Coach.query.with_deleted().all():
    db.session.delete(coach)

for tourn in Tournament.query.all():
    db.session.delete(tourn)

db.session.commit()
