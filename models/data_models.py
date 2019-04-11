from .base_model import db, Base, QueryWithSoftDelete
import datetime
import logging
import os
from sqlalchemy import event

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('transaction')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, '../logs/transaction.log'), encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Card(Base):
    __tablename__ = 'cards'

    name = db.Column(db.String(80), nullable=False,supports_json = True)
    description = db.Column(db.Text(),supports_json = True)
    race = db.Column(db.String(20), nullable=False,supports_json = True)
    rarity = db.Column(db.String(20), nullable=False,supports_json = True)
    card_type = db.Column(db.String(20), nullable=False,supports_json = True)
    subtype = db.Column(db.String(30), nullable=False,supports_json = True)
    notes = db.Column(db.String(255),supports_json = True)

    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'), nullable=False)

    def __repr__(self):
        return '<Card %r>' % self.name

class Pack(Base):
    __tablename__ = 'packs'

    pack_type = db.Column(db.String(20), nullable=False,supports_json = True)
    price = db.Column(db.Integer, default=0, nullable=False,supports_json = True)
    team = db.Column(db.String(20),supports_json = True)

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transaction = db.relationship('Transaction',uselist=False, backref=db.backref('pack', lazy=True), cascade="all, delete-orphan",supports_json = True,lazy=False)
    cards = db.relationship('Card', backref=db.backref('pack', lazy=False), cascade="all, delete-orphan",supports_json = True,lazy=False)

    def __repr__(self):
        return '<Pack %r>' % self.pack_type

class Coach(Base):  
    __tablename__ = 'coaches'
    name = db.Column(db.String(80), unique=True, nullable=False,supports_json = True)
    deleted_name = db.Column(db.String(80), unique=False, nullable=True)
    account = db.relationship('Account', uselist=False, backref=db.backref('coach', lazy=False), cascade="all, delete-orphan",supports_json = True)
    packs = db.relationship('Pack', backref=db.backref('coach', lazy=False),cascade="all, delete-orphan",supports_json = True,lazy=False)
    cards = db.relationship('Card', secondary="packs",backref=db.backref('coach', lazy=False, uselist=False), viewonly=True,lazy=False)
    deleted = db.Column(db.Boolean(), default=False)

    query_class = QueryWithSoftDelete

    def __init__(self,name):
        self.name = name
        self.account = Account()

    def __repr__(self):
        return '<Coach %r>' % self.name

    def short_name(self):
        return self.name[:-5]

    def discord_id(self):
        return self.name[-4:]

    def make_transaction(self,transaction):
        # do nothing
        if self.account.amount < transaction.price:
            raise TransactionError("Insuficient Funds")
        if transaction.confirmed:
            raise TransactionError("Double processing of transaction")

        try:
            self.account.amount = self.account.amount - transaction.price
            transaction.confirm()
            self.account.transactions.append(transaction)
            if transaction.pack is not None:
                transaction.pack.coach = self
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            raise TransactionError(str(e))
        else:
            logger.info(f"{self.name}: {transaction.description} for {transaction.price}")

        return transaction

    # soft delete
    def remove(self):
        try:
            self.deleted = True
            self.deleted_name = self.name
            self.name = f"{self.name}_{self.id}"
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            raise TransactionError(str(e))
        else:
            logger.info(f"{self.deleted_name}: Coach soft deleted")

    # restore data after the soft delete
    def restore(self):
        try:
            self.deleted = False
            self.name = self.deleted_name
            self.deleted_name = None
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            raise TransactionError(str(e))
        else:
            logger.info(f"{self.name}: Coach restored")

    # soft deletes a coach adn reset its account to fresh one
    def reset(self):
        try:
            name = self.name
            self.remove()
            new_coach=self.__class__.create(name)
        except Exception as e:
            raise TransactionError(str(e))
        else:
            logger.info(f"{new_coach.name}: Coach reset")
        return new_coach

    @classmethod
    def get_by_name(cls,name):
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def create(cls,name):
        coach = cls(name)
        db.session.add(coach)
        db.session.commit()
        return coach

    @classmethod
    def find_all_by_name(cls,name):
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
        
class Account(Base):
    __tablename__ = 'accounts'
    INIT_CASH = 10
    amount = db.Column(db.Integer, default=INIT_CASH, nullable=False,supports_json = True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transactions = db.relationship('Transaction', backref=db.backref('Account', lazy=False), cascade="all, delete-orphan",supports_json = True,lazy=False)

    def __repr__(self):
        return '<Account %r>' % self.amount

class Transaction(Base):
    __tablename__ = 'transactions'

    date_confirmed = db.Column(db.DateTime,  nullable=True,supports_json = True)
    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'))
    price = db.Column(db.Integer, default=0, nullable=False,supports_json = True)
    confirmed = db.Column(db.Boolean, default = False, nullable=False,supports_json = True)
    description = db.Column(db.String(255), nullable=False,supports_json = True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    def confirm(self):
        self.confirmed = True
        self.date_confirmed = datetime.datetime.now()


class TransactionError(Exception):
    pass

AUTO_CARDS = {
    'Loose Change!':5,
    'Bank Error!':10,
    'Lottery Win!':15
}
#checks the pack for cards that can be auto processed
def pack_checker(session, flush_context, instances):
    print(session.new)
    #for card in pack.cards:
    #    if card.name in AUTO_CARDS.keys():
    #        amount = AUTO_CARDS[card.name]
    #        reason = f'{card.name} autoprocessing'
    #        t = Transaction(description=reason,price=-1*amount)
    #        try:
    #            coach.make_transaction(t)
    #        except TransactionError as e:
    #            await self.transaction_error(e)
    #            return
    #        else:

event.listen(db.session, "before_flush", pack_checker)
