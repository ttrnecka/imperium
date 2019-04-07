from .base_model import db, Base
import datetime
import logging
import os

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('transaction')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, '../logs/transaction.log'), encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Card(Base):
    __tablename__ = 'cards'

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    subtype = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(255))

    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'), nullable=False)

    def __repr__(self):
        return '<Card %r>' % self.name

class Pack(Base):
    __tablename__ = 'packs'

    pack_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, default=0, nullable=False)
    team = db.Column(db.String(20))

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transaction = db.relationship('Transaction',uselist=False, backref=db.backref('pack', lazy=True), cascade="all, delete-orphan")
    cards = db.relationship('Card', backref=db.backref('pack', lazy=False), cascade="all, delete-orphan")

    def __repr__(self):
        return '<Pack %r>' % self.pack_type

class Coach(Base):  
    __tablename__ = 'coaches'
    name = db.Column(db.String(80), unique=True, nullable=False)
    account = db.relationship('Account', uselist=False, backref=db.backref('coach', lazy=True), cascade="all, delete-orphan")
    packs = db.relationship('Pack', backref=db.backref('coach', lazy=False),cascade="all, delete-orphan")
    cards = db.relationship('Card', secondary="packs",backref=db.backref('coach', lazy=False, uselist=False,), viewonly=True)

    def __init__(self,name):
        self.name = name
        self.account = Account()

    def __repr__(self):
        return '<Coach %r>' % self.name

    def short_name(self):
        return self.name[:-5]

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
    INIT_CASH = 15 
    amount = db.Column(db.Integer, default=INIT_CASH, nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transactions = db.relationship('Transaction', backref=db.backref('Account', lazy=True), cascade="all, delete-orphan")

    def __repr__(self):
        return '<Account %r>' % self.amount

class Transaction(Base):
    __tablename__ = 'transactions'

    date_confirmed = db.Column(db.DateTime,  nullable=True)
    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'))
    price = db.Column(db.Integer, default=0, nullable=False)
    confirmed = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(20), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    def confirm(self):
        self.confirmed = True
        self.date_confirmed = datetime.datetime.now()


class TransactionError(Exception):
    pass
