from web import db, create_app
from models.models import Coach, Account, Card, Pack, Transaction
import imperiumbase as ib

app = create_app()
app.app_context().push()

# for each coach
for coach_data in ib.Coach.all():
    coach = Coach(name=coach_data.name)
    acc = Account(amount=coach_data.account.cash, coach=coach)
    for transaction in coach_data.account.transactions:
        tr = Transaction(confirmed = transaction.confirmed,price = transaction.price)
        if isinstance(transaction.comodity, ib.Pack):
            tr.description = transaction.comodity.description()
            p = transaction.comodity
            pack = Pack(pack_type=p.pack_type,price=p.price)
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
