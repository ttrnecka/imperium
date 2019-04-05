from .base_model import db, Base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import case

class Card(Base):
    __tablename__ = 'cards'

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    subtype = db.Column(db.String(30), nullable=False)

    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'), nullable=False)
    pack = db.relationship('Pack', backref=db.backref('cards', lazy=True))

rarity_sort = {"Common:": 4, "Rare": 3, "Epic": 2, "Legendary": 1}
sort_order = case(value=Card.rarity, whens=rarity_sort)

class Coach(Base):
    __tablename__ = 'coaches'
    name = db.Column(db.String(80), unique=True, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    account = db.relationship('Account', backref=db.backref('coach', lazy=True, uselist=False))

    def __repr__(self):
        return '<Coach %r>' % self.name

    @hybrid_property
    def cards(self):
        cards = []
        for pack in self.packs:
            cards.extend(pack.cards)
        return cards


class Account(Base):
    __tablename__ = 'accounts'
    amount = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.amount

class Pack(Base):
    __tablename__ = 'packs'

    pack_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, default=0, nullable=False)

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    coach = db.relationship('Coach', backref=db.backref('packs', lazy=True))

class Transaction(Base):
    __tablename__ = 'transactions'

    date_confirmed = db.Column(db.DateTime,  nullable=True)
    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'))
    pack = db.relationship('Pack', backref=db.backref('transaction', lazy=True, uselist=False))
    price = db.Column(db.Integer, default=0, nullable=False)
    confirmed = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(20), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    account = db.relationship('Account', backref=db.backref('transactions', lazy=True))
