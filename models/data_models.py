from .base_model import db, Base, QueryWithSoftDelete
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
from sqlalchemy import UniqueConstraint, event
from sqlalchemy.dialects import mysql 

ROOT = os.path.dirname(__file__)

logger = logging.getLogger('transaction')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(ROOT, '../logs/transaction.log'), encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

db_logger = logging.getLogger("DB logging")
db_logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(ROOT, '../logs/db.log'), maxBytes=10000000, backupCount=5, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
db_logger.addHandler(handler)

class Card(Base):
    __tablename__ = 'cards'

    name = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text())
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    subtype = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(255))

    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'), nullable=False)
    duster_id = db.Column(db.Integer, db.ForeignKey('dusters.id'))

    def __repr__(self):
        return f'<Card {self.name}, rarity: {self.rarity}, pack_id: {self.pack_id}>'

class Pack(Base):
    __tablename__ = 'packs'

    pack_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, default=0, nullable=False)
    team = db.Column(db.String(20))

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transaction = db.relationship('Transaction',uselist=False, backref=db.backref('pack', lazy=True), cascade="all, delete-orphan",lazy=False)
    cards = db.relationship('Card', backref=db.backref('pack', lazy=False), cascade="all, delete-orphan",lazy=False)

    def __repr__(self):
        return f'<Pack {self.pack_type}>'

class Coach(Base):  
    __tablename__ = 'coaches'
    # long discord id
    disc_id = db.Column(db.BigInteger(),nullable=False,index=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    deleted_name = db.Column(db.String(80), unique=False, nullable=True)
    account = db.relationship('Account', uselist=False, backref=db.backref('coach', lazy=True), cascade="all, delete-orphan")
    packs = db.relationship('Pack', backref=db.backref('coach', lazy=True),cascade="all, delete-orphan",lazy="subquery")
    cards = db.relationship('Card', secondary="packs",backref=db.backref('coach', lazy=True, uselist=False), viewonly=True,lazy="subquery")
    deleted = db.Column(db.Boolean(), default=False)
    duster = db.relationship("Duster", backref=db.backref('coach'), cascade="all, delete-orphan",uselist=False)
    web_admin = db.Column(db.Boolean(), default=False)

    query_class = QueryWithSoftDelete

    def __init__(self,name="",disc_id=0):
        self.name = name
        self.disc_id = disc_id
        self.account = Account()

    def __repr__(self):
        return '<Coach %r>' % self.name

    def short_name(self):
        return self.name[:-5]

    # id behind #
    def discord_id(self):
        return self.name[-4:]

    def make_transaction(self,transaction):
        # do nothing
        if self.account.amount < transaction.price:
            raise TransactionError("Insuficient Funds")
        if transaction.confirmed:
            raise TransactionError("Double processing of transaction")

        try:
            self.account.amount = Account.amount - transaction.price
            transaction.confirm()
            self.account.transactions.append(transaction)
            if transaction.pack is not None:
                transaction.pack.coach = self
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
    def get_by_discord_id(cls,id):
        return cls.query.filter_by(disc_id=id).one_or_none()

    @classmethod
    def create(cls,name,disc_id):
        coach = cls(name,disc_id)
        db.session.add(coach)
        db.session.commit()
        return coach

    @classmethod
    def find_all_by_name(cls,name):
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
        
class Account(Base):
    __tablename__ = 'accounts'
    INIT_CASH = 10
    amount = db.Column(db.Integer, default=INIT_CASH, nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transactions = db.relationship('Transaction', backref=db.backref('account', lazy=False), cascade="all, delete-orphan",lazy=False)

    def __repr__(self):
        return '<Account %r>' % self.amount

class Transaction(Base):
    __tablename__ = 'transactions'

    date_confirmed = db.Column(db.DateTime,  nullable=True)
    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'))
    price = db.Column(db.Integer, default=0, nullable=False)
    confirmed = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    def confirm(self):
        self.confirmed = True
        self.date_confirmed = datetime.datetime.now()


class TournamentSignups(Base):
    __tablename__ = 'tournaments_signups'

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    # mode used to separate reserve signups
    mode = db.Column(db.String(20),nullable=True)

    __table_args__ = (
        UniqueConstraint('tournament_id', 'coach_id', name='uix_tournament_id_coach_id'),
    )

    tournament = db.relationship("Tournament", backref=db.backref('tournament_signups', cascade="all, delete-orphan"))
    coach = db.relationship("Coach", backref=db.backref('tournament_signups', cascade="all, delete-orphan"))

class Tournament(Base):
    __tablename__ = 'tournaments'

    tournament_id = db.Column(db.Integer,nullable=False, index=True, unique=True)
    name = db.Column(db.String(255),nullable=False, index=True)
    discord_channel = db.Column(db.String(255),nullable=True)
    type = db.Column(db.String(80),nullable=False)
    mode = db.Column(db.String(80),nullable=False)
    signup_close_date = db.Column(db.String(80),  nullable=True)
    expected_start_date = db.Column(db.String(80),  nullable=True)
    expected_end_date = db.Column(db.String(80),  nullable=True)
    deadline_date = db.Column(db.String(80),  nullable=True)
    fee = db.Column(db.Integer(),default=0,nullable=False)
    status = db.Column(db.String(80),nullable=False)
    coach_limit = db.Column(db.Integer(),default=4, nullable=False)
    reserve_limit = db.Column(db.Integer(),default=0, nullable=False)
    region = db.Column(db.String(80),nullable=False)
    deck_limit =  db.Column(db.Integer(), default=18, nullable=False)
    admin =  db.Column(db.String(80),nullable=True)
    sponsor = db.Column(db.String(80),nullable=True)
    sponsor_description = db.Column(db.Text,nullable=True)
    special_rules = db.Column(db.Text(),nullable=True)
    prizes = db.Column(db.Text(),nullable=True)
    unique_prize = db.Column(db.Text,nullable=True)

    coaches = db.relationship("Coach", secondary="tournaments_signups", backref=db.backref('tournaments', lazy="dynamic"), lazy="dynamic")

class TransactionError(Exception):
    pass

class Duster(Base):
    __tablename__ = 'dusters'

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False, unique=True) 
    cards = db.relationship('Card', backref=db.backref('duster', lazy=True),lazy=False)
    status = db.Column(db.String(80),nullable=False)
    type = db.Column(db.String(80),nullable=True)

    def __init__(self,status="OPEN"):
        self.status = status
    

@event.listens_for(Card, 'after_delete')
@event.listens_for(Duster, 'after_delete')
def receive_after_delete(mapper, connection, target):
    db_logger.info(f"Deleted {target.__dict__}")

@event.listens_for(Card, 'after_insert')
@event.listens_for(Duster, 'after_insert')
def receive_after_insert(mapper, connection, target):
    db_logger.info(f"Created {target.__dict__}")
