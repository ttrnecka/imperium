from web import db, create_app
from models.data_models import Coach, Account,Transaction, Pack, Card
import imperiumbase as ib
from datetime import datetime

app = create_app()
app.app_context().push()

# for each coach
for coach_data in ib.Coach.all():
    coach = Coach(name=coach_data.name)
    acc = Account(amount=coach_data.account.cash, coach=coach)
    for transaction in coach_data.account.transactions:
        tr = Transaction(confirmed = transaction.confirmed,price = transaction.price)
        tr.date_created = datetime.utcfromtimestamp(transaction.created_at)
        tr.date_confirmed = datetime.utcfromtimestamp(transaction.confirmed_at)
        if isinstance(transaction.comodity, ib.Pack):
            tr.description = transaction.comodity.description()
            p = transaction.comodity
            if hasattr(p,'team'):
                team = p.team
            else:
                team = None
            pack = Pack(pack_type=p.pack_type,price=p.price,team=team)
            pack.coach=coach
            pack.transaction=tr
            for card in p.cards:
                cc = Card(
                    name = card["Card Name"],
                    description = card["Description"],
                    card_type = card["Type"],
                    subtype = card["Subtype"],
                    rarity = card["Rarity"],
                    race = card["Race"]
                )
                pack.cards.append(cc)
        else:
            tr.description = transaction.comodity
    
        acc.transactions.append(tr)
    db.session.add(coach)
db.session.commit()
