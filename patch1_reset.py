# Works with Python 3.6
from web import db, create_app
from models.data_models import  Account, Pack, Transaction, Coach

app = create_app()
app.app_context().push()

for coach in Coach.query.with_deleted().all():
    coach.packs[:] = []

# set all accounts to 10
for account in Account.query.all():
    account.amount=10
    account.transactions[:] = []

db.session.commit()