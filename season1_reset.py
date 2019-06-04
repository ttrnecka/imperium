# Works with Python 3.6
from web import db, create_app
from models.data_models import  Account, Pack, Transaction, Coach

app = create_app()
app.app_context().push()

for coach in Coach.query.with_deleted().all():
    db.session.delete(coach)

db.session.commit()