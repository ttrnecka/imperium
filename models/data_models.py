from .base_model import db, Base, QueryWithSoftDelete
from .achievements import achievements_template
import datetime
import logging
import json
from logging.handlers import RotatingFileHandler
import os
from sqlalchemy import UniqueConstraint, event
from sqlalchemy.dialects import mysql 
from sqlalchemy.types import TypeDecorator
from sqlalchemy.sql.expression import func
from misc.base_statline import base_statline


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

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class TextPickleType(TypeDecorator):
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value not in [None,""]:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value not in [None,""]:
            value = json.loads(value)
        return value

class CardTemplate(Base):
    __tablename__ = 'card_templates'

    TYPE_PLAYER = "Player"
    TYPE_TRAINING = "Training"
    TYPE_SP = "Special Play"
    TYPE_STAFF = "Staff"
    RARITY_LEGEND = "Legendary"
    RARITY_UNIQUE = "Unique"
    RARITY_INDUCEMENT = "Inducement"
    RARITY_COMMON = "Common"
    RARITY_EPIC = "Epic"
    SUBTYPE_LINEMAN = "Lineman"
    SUBTYPE_BASIC = "Basic"
    SUBTYPE_SPECIALIZED = "Specialized"
    SUBTYPE_CORE = "Core"

    name = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text())
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False, index=True)
    card_type = db.Column(db.String(20), nullable=False, index=True)
    subtype = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(255))
    value = db.Column(db.Integer, nullable=False, default=1)
    skill_access = db.Column(db.String(20))
    multiplier = db.Column(db.Integer(), nullable=False, default=1)
    starter_multiplier = db.Column(db.Integer(), nullable=False, default=0)
    one_time_use = db.Column(db.Boolean(), default=False, nullable=False)
    position = db.Column(db.String(50), nullable=False)

    cards = db.relationship('Card', backref=db.backref('template', lazy="selectin"), cascade="all, delete-orphan",lazy=True)

    def __init__(self,**kwargs):
        super(CardTemplate, self).__init__(**kwargs)
        
    def __repr__(self):
        return f'<CardTemplate {self.id}. {self.name}, rarity: {self.rarity}, type: {self.card_type}>'

class Card(Base):
    __tablename__ = 'cards'

    name = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text())
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    subtype = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(255))
    value = db.Column(db.Integer, nullable=False, default=1)
    deck_type = db.Column(db.String(255), nullable=False, default="base")

    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'), nullable=False)
    duster_id = db.Column(db.Integer, db.ForeignKey('dusters.id'))

    in_development_deck = db.Column(db.Boolean(), default=False)
    in_imperium_deck = db.Column(db.Boolean(), default=False)
    assigned_to = db.Column(db.String(255),default="")
    assigned_to_array = db.Column(TextPickleType(), nullable=False, default=json.dumps({}))
    uuid = db.Column(db.String(255),default="", index=True)
    skill_access = db.Column(db.String(20))

    card_template_id = db.Column(db.Integer, db.ForeignKey('card_templates.id'), index=True, nullable=True)

    is_starter = db.Column(db.Boolean(), default=False)

    def get(self, name, show_hidden=True):
        if not show_hidden and self.template.card_type == "Reaction" and \
                name in ["name","description"]:
            return "Reaction"
        return getattr(self.template,name)

    def __init__(self,**kwargs):
        super(Card, self).__init__(**kwargs)
        self.assigned_to_array = {}
    
    def _template(self, template):
        """When using template clear the other values, they will be removed in later phase TODO"""
        for attribute in ["name", "description", "race", "rarity", "card_type", "subtype", "notes", "value", "skill_access"]:
            setattr(self, attribute, "")
        self.template = template
        
    def statline(self):
        return base_statline.get(f"{self.first_race()}_{self.template.position}","")
    
    def first_race(self):
        return self.template.race.split('/')[0]

    def strength(self):
        return self.stat(1)

    def movement(self):
        return self.stat(0)
    
    def agility(self):
        return self.stat(2)
    
    def armour(self):
        return self.stat(3)

    def stunty(self):
        if len(self.statline()) == 5 and self.statline()[4].lower() == "s":
            return True
        return False

    def stat(self,index):
        return int(self.statline()[index],16) if self.statline() else None

    def __repr__(self):
        return f'<Card {self.template.name}, rarity: {self.template.rarity}, pack_id: {self.pack_id}>'

    @classmethod
    def from_template(cls, template):
        model = cls()
        model._template(template)
        return model

class Pack(Base):
    __tablename__ = 'packs'

    pack_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, default=0, nullable=False)
    team = db.Column(db.String(20))
    season = db.Column(db.String(20), default="1", nullable=False, index=True)

    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)

    transaction = db.relationship('Transaction',uselist=False, backref=db.backref('pack', lazy="select"), cascade="all, delete-orphan",lazy="select")
    cards = db.relationship('Card', backref=db.backref('pack', lazy="select"), cascade="all, delete-orphan",lazy="selectin")

    def __repr__(self):
        return f'<Pack {self.pack_type}>'

    def __init__(self,**kwargs):
        super(Pack, self).__init__(**kwargs)
        self.season = db.get_app().config["SEASON"]

class Coach(Base):  
    __tablename__ = 'coaches'
    # long discord id
    disc_id = db.Column(db.BigInteger(),nullable=False,index=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    deleted_name = db.Column(db.String(80), unique=False, nullable=True)
    account = db.relationship('Account', uselist=False, backref=db.backref('coach', lazy=True), cascade="all, delete-orphan",lazy="selectin")
    packs = db.relationship('Pack', backref=db.backref('coach', lazy=True),cascade="all, delete-orphan",lazy="select")
    cards = db.relationship('Card', secondary="packs",backref=db.backref('coach', lazy=True, uselist=False), viewonly=True,lazy="select")
    deleted = db.Column(db.Boolean(), default=False)
    duster = db.relationship("Duster", backref=db.backref('coach'), cascade="all, delete-orphan",uselist=False)
    web_admin = db.Column(db.Boolean(), default=False)
    bb2_name = db.Column(db.String(80), unique=True, nullable=True, index=True)
    achievements = db.Column(TextPickleType(), nullable=True)
    free_packs = db.Column(db.Text(), nullable=False, default="")

    query_class = QueryWithSoftDelete

    def __init__(self,name="",disc_id=0):
        self.name = name
        self.disc_id = disc_id
        self.account = Account()
        self.free_packs = "player"
        self.achievements = achievements_template

    def __repr__(self):
        return '<Coach %r>' % self.name

    def active(self):
        return not self.deleted

    def activate(self):
        self.deleted = False
        self.free_packs = "player"

    def short_name(self):
        return self.name[:-5]

    def collection_value(self):
        return sum([card.get('value') for card in self.active_cards() if not card.is_starter])

    # id behind #
    def discord_id(self):
        return self.name[-4:]

    def mention(self):
        return f'<@{self.disc_id}>'

    def earned(self):
        cash = 0
        for tr in self.account.transactions:
            if tr.price<0 and tr.season==db.get_app().config['SEASON']:
                cash += -1*tr.price
        return cash

    def stats(self):
        app = db.get_app()
        store = os.path.join(ROOT, '..', 'data', f"season{app.config['SEASON']}")
        stats_file = os.path.join(store,"stats.json")
        if os.path.isfile(stats_file):
            f = open(stats_file, "r")
            data = json.loads(f.read())
            if self.bb2_name:
                stats = data['coaches'].get(self.bb2_name, {})
                return stats
        return {}

    def active_cards(self):
        return Card.query.join(Card.pack).filter(Pack.coach_id == self.id).filter(Pack.season == db.get_app().config["SEASON"]).all()
        #cards = []
        #for card in self.cards:
        #    if card.pack.season==db.get_app().config['SEASON']:
        #        cards.append(card)
        #return cards

    def inactive_cards(self):
        return Card.query.join(Card.pack).filter(Pack.coach_id == self.id).filter(Pack.season == db.get_app().config["PREVIOUS_SEASON"]).all()

    def make_transaction(self,transaction, commit=True):
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
            if commit:
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
            disc_id = self.disc_id
            self.remove()
            new_coach=self.__class__.create(name,disc_id)
        except Exception as e:
            raise TransactionError(str(e))
        else:
            logger.info(f"{new_coach.name}: Coach reset")
        return new_coach
    
    def grant(self,item=0,description="", commit=True):
        if RepresentsInt(item):
            t = Transaction(description=description,price=-1*int(item))
            try:
                self.make_transaction(t, commit=commit)
            except TransactionError as e:
                return False, e
            else:
                return True, ""
        else:
            t = Transaction(description=description,price=0)
            self.add_to_freepacks(item)
            self.make_transaction(t, commit=commit)
            return True, ""

    def get_freepacks(self):
        return [pack for pack in self.free_packs.split(',') if pack!='']

    def set_freepacks(self,list):
        self.free_packs=(',').join(list)
        return self.free_packs

    def add_to_freepacks(self,pack):
        packs = self.get_freepacks()
        packs.append(pack)
        self.set_freepacks(packs)
    
    def remove_from_freepacks(self,pack):
        packs = self.get_freepacks()
        packs.remove(pack)
        self.set_freepacks(packs)


    @classmethod
    def get_by_discord_id(cls,id, deleted=False):
        if deleted:
            return cls.query.with_deleted().filter_by(disc_id=id).one_or_none()
        else:
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

    transactions = db.relationship('Transaction', backref=db.backref('account', lazy=False), cascade="all, delete-orphan", lazy='select')

    def __repr__(self):
        return '<Account %r>' % self.amount

    def reset(self):
        self.amount = self.__class__.INIT_CASH

class Transaction(Base):
    __tablename__ = 'transactions'

    date_confirmed = db.Column(db.DateTime,  nullable=True)
    pack_id = db.Column(db.Integer, db.ForeignKey('packs.id'))
    price = db.Column(db.Integer, default=0, nullable=False)
    confirmed = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    season = db.Column(db.String(20), default="1", nullable=False, index=True)

    def confirm(self):
        self.confirmed = True
        self.date_confirmed = datetime.datetime.now()

    def __init__(self,**kwargs):
        super(Transaction, self).__init__(**kwargs)
        self.season = db.get_app().config["SEASON"]

deck_card_table = db.Table('deck_cards', Base.metadata,
    db.Column('deck_id', db.Integer, db.ForeignKey('decks.id')),
    db.Column('card_id', db.Integer, db.ForeignKey('cards.id'))
)

class Deck(Base):
    __tablename__ = 'decks'

    team_name = db.Column(db.String(255),nullable=False)
    mixed_team = db.Column(db.String(255),nullable=False)
    cards = db.relationship("Card", secondary=deck_card_table, backref=db.backref('decks', lazy="dynamic"), lazy="dynamic")

    commited = db.Column(db.Boolean(), default=False)
    extra_cards = db.Column(TextPickleType(), nullable=False)
    unused_extra_cards = db.Column(TextPickleType(), nullable=False)
    comment = db.Column(db.Text(),nullable=False, default="")
    log = db.Column(db.Text(),nullable=False, default="")
    injury_map = db.Column(TextPickleType(), nullable=False)
    phase_done = db.Column(db.Boolean(), default=False)

    def deck_upgrade_cards(self):
        return [card for card in self.tournament_signup.coach.active_cards() if card.template.subtype=="Deck Upgrade"]

    def to_log(self,msg):
        if self.commited:
            self.log += msg
            self.log +="\n"

class TournamentSignups(Base):
    __tablename__ = 'tournaments_signups'

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=True)

    # mode used to separate reserve signups
    mode = db.Column(db.String(20),nullable=True)

    __table_args__ = (
        UniqueConstraint('tournament_id', 'coach_id', name='uix_tournament_id_coach_id'),
    )

    tournament = db.relationship("Tournament", backref=db.backref('tournament_signups', cascade="all, delete-orphan"), foreign_keys=[tournament_id])
    coach = db.relationship("Coach", backref=db.backref('tournament_signups', cascade="all, delete-orphan", lazy=False) ,foreign_keys=[coach_id], lazy='select')
    deck = db.relationship("Deck", backref=db.backref('tournament_signup',uselist=False), single_parent=True, cascade="all, delete-orphan", foreign_keys=[deck_id])

class Tournament(Base):
    __tablename__ = 'tournaments'

    PHASES = [
        "deck_building",
        "locked",
        "special_play",
        "inducement",
        "blood_bowl"
    ]

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
    phase = db.Column(db.String(255),nullable=False, default="deck_building")
    deck_value_limit =  db.Column(db.Integer(), default=150, nullable=False)
    consecration =  db.Column(db.String(80),nullable=True)
    corruption =  db.Column(db.String(80),nullable=True)

    coaches = db.relationship("Coach", secondary="tournaments_signups", backref=db.backref('tournaments', lazy="dynamic"), lazy="dynamic")

    def is_full(self):
        if len(self.tournament_signups) >= self.coach_limit + self.reserve_limit:
            return True
        else:
            return False

    def can_auto_start(self):
        # can autostart just devs boot camps and regulars
        typ = self.type.lower()
        mode = self.mode.lower()
        if typ == "development" and mode in ["boot camp", "regular"]:
            return True
        return False

class TournamentTemplate(Base):
    __tablename__ = 'tournament_templates'

    active = db.Column(db.Boolean(),nullable=False, default=True)
    type = db.Column(db.String(80),nullable=False)
    mode = db.Column(db.String(80),nullable=False)
    coach_limit = db.Column(db.Integer(),default=4, nullable=False)
    deck_limit =  db.Column(db.Integer(), default=18, nullable=False)
    deck_value_limit =  db.Column(db.Integer(), default=150, nullable=False)
    prizes = db.Column(db.Text(),nullable=True)

class TournamentAdmin(Base):
    __tablename__ = 'tournament_admins'

    name = db.Column(db.String(80),nullable=False)
    region = db.Column(db.String(255),nullable=False)
    load = db.Column(db.Integer(),default=2, nullable=False)
    tournament_types = db.Column(db.String(255),nullable=False)

class TournamentSponsor(Base):
    __tablename__ = 'tournament_sponsors'

    name = db.Column(db.String(80),nullable=False)
    effect = db.Column(db.Text(),nullable=False)
    skill_pack_granted = db.Column(db.String(255),nullable=True)
    special_rules = db.Column(db.Text(),nullable=False)

class TournamentRoom(Base):
    __tablename__ = 'tournament_rooms'

    name = db.Column(db.String(80),nullable=False)

class ConclaveRule(Base):
    __tablename__ = 'conclave_rules'

    type = db.Column(db.String(80),nullable=False)
    name = db.Column(db.String(80),nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    level1 = db.Column(db.Integer(), nullable=False)
    level2 = db.Column(db.Integer(), nullable=False)
    level3 = db.Column(db.Integer(), nullable=False)
    notes = db.Column(db.Text(), nullable=False)

    @classmethod
    def consecrations(cls):
        return cls._get_type("Consecration")

    @classmethod
    def corruptions(cls):
        return cls._get_type("Corruption")

    @classmethod
    def blessings(cls):
        return cls._get_type("Blessing")

    @classmethod
    def curses(cls):
        return cls._get_type("Curse")

    @classmethod
    def _get_type(cls,cr_type):
        return cls.query.filter_by(type=cr_type).all()

    def same_class(self,rule):
        """Returns true if self is same class as the provided rule"""
        if self.klass() == rule.klass():
            return True
        return False

    def klass(self):
        """Return the klass of the rule"""
        return self.name.replace("Consecration of ","").replace("Corruption of ","").replace("Blessing of ","").replace("Curse of ","").replace("the ","").replace("-","_")
    

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
    

class CrackerCardTemplate(Base):
    __tablename__ = 'cracker_card_templates'

    RACE_DICT = {
        "au": "MercenaryUndead",
        "sbr": "MercenaryAristo",
        "uosp": "MercenaryStunty",
        "vt": "MercenarySavage",
        "egc": "MercenaryElf",
        "cgs": "MercenaryChaosGods",
        "fea": "MercenaryEasterners",
        "afs": "MercenaryExplorers",
        "hl": "MercenaryHuman",
        "aog": "MercenaryGoodGuys",
        "cpp": "MercenaryChaos"
    }

    name = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text())
    race = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False, index=True)
    card_type = db.Column(db.String(20), nullable=False, index=True)
    klass = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.String(255))
    team = db.Column(db.String(30), nullable=False)
    multiplier = db.Column(db.Integer(), nullable=False, default=1)
    one_time_use = db.Column(db.Boolean(), default=False, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    built_in_skill = db.Column(db.String(255))
    
    cards = db.relationship('CrackerCard', backref=db.backref('cracker_template', lazy="selectin"), cascade="all, delete-orphan",lazy=True)

    def __init__(self,**kwargs):
        super(CrackerCardTemplate, self).__init__(**kwargs)
        
    def __repr__(self):
        return f'<CrackerCardTemplate {self.id}. {self.name}, rarity: {self.rarity}, type: {self.card_type}>'

    def cyanide_player_type(self):
        if self.card_type == 'Positional':
            return f"{self.cyanide_mixed_race_name()}_{self.cyanide_race_name()}_{self.cyanide_position_name()}"
        return "not_applicable"

    def cyanide_position_name(self):
        return self.position.replace(" ","")

    def cyanide_race_name(self):
        race = self.race.replace(" ", "")
        if race == "Bretonnian":
            race = "Bretonnia"
        return race
        
    def cyanide_mixed_race_name(self):
        race = self.team.lower()
        return self.RACE_DICT.get(race, "Unknown")

class CrackerCard(Base):
    __tablename__ = 'cracker_cards'

    team_id = db.Column(db.Integer, db.ForeignKey('cracker_team.id'), index=True, nullable=False)
    pack_id = db.Column(db.Integer(), index=True, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('cracker_card_templates.id'), index=True, nullable=False)

    def __init__(self,**kwargs):
        super(CrackerCard, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Card {self.cracker_template.name}, rarity: {self.cracker_template.rarity}>'

    def _template(self, template):
        self.cracker_template = template

    def coach(self):
        return self.team.coach
        
    @classmethod
    def from_template(cls, template):
        model = cls()
        model._template(template)
        return model

    @classmethod
    def max_pack_id(cls):
        return db.session.query(func.max(CrackerCard.pack_id)).scalar()

class CrackerTeam(Base):
    __tablename__ = 'cracker_team'
    
    coach = db.Column(db.String(255), index=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    cards = db.relationship('CrackerCard', backref=db.backref('team', lazy=True), cascade="all, delete-orphan",lazy="selectin")
        

@event.listens_for(Card, 'after_delete')
@event.listens_for(Duster, 'after_delete')
def receive_after_delete(mapper, connection, target):
    db_logger.info(f"Deleted {target.__dict__}")

@event.listens_for(Card, 'after_insert')
@event.listens_for(Duster, 'after_insert')
def receive_after_insert(mapper, connection, target):
    db_logger.info(f"Created {target.__dict__}")


def date_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@event.listens_for(Deck.mixed_team,'set')
def log_deck_team(target, value, oldvalue, initiator):
    if value!=oldvalue:
        target.to_log(f"{date_now()}: Mixed team changed from {oldvalue} to {value}")

@event.listens_for(Deck.team_name,'set')
def log_deck_team_name(target, value, oldvalue, initiator):
    if value!=oldvalue:
        target.to_log(f"{date_now()}: Team name changed from {oldvalue} to {value}")

@event.listens_for(Deck.commited,'set')
def log_deck_committed(target, value, oldvalue, initiator):
    if value!=oldvalue:
        target.to_log(f"{date_now()}: Deck committed")

@event.listens_for(Deck.cards, 'append', propagate=True)
def log_deck_cards_append(target, value, initiator):
    target.to_log(f"{date_now()}: Card {value.name} added to the deck")

@event.listens_for(Deck.cards, 'remove', propagate=True)
def log_deck_cards_remove(target, value, initiator):
    target.to_log(f"{date_now()}: Card {value.name} removed from the deck")

