from flask_marshmallow import Marshmallow
from .data_models import Transaction, Account, Card, Coach, Tournament, TournamentSignups, Duster, Deck, CrackerCard, CrackerCardTemplate, HighCommand
from .data_models import CardTemplate, HighCommandSquad
from marshmallow_sqlalchemy import ModelSchema

ma = Marshmallow()

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction

class HighCommandSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HighCommand

class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account
    #transactions = ma.Nested(TransactionSchema, many=True)
    transactions = ma.Nested(TransactionSchema, many=True, attribute = 'last_transactions')

class CardTemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CardTemplate
        exclude = ["cards"]
    date_modified = ma.String()
    date_created = ma.String()

class CardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Card
        exclude = ["decks", "coach"]
    assigned_to_array = ma.Dict(ma.List(ma.String))
    template = ma.Nested(CardTemplateSchema)
    default_skills = ma.List(ma.String())
    coach_data = ma.Dict(attribute = 'coach_dict')

class HighCommandSquadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HighCommandSquad
        include_relationships = True
    level = ma.Integer()
    cards = ma.Nested(CardSchema, many=True)

class TournamentSignupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TournamentSignups
    coach = ma.Integer(attribute = 'coach_id')
    deck = ma.Integer(attribute = 'deck_id')

class TournamentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tournament
        exclude = ["coaches"]
    tournament_signups = ma.Nested(TournamentSignupSchema, many=True)
    conclave_ranges = ma.Dict()

class DusterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Duster
        include_relationships = True

class CoachSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Coach
        exclude = ["packs"]
        include_relationships = True
    
    account = ma.Nested(AccountSchema)
    duster = ma.Nested(DusterSchema)
    short_name = ma.String()
    achievements = ma.Dict()
    stats = ma.Dict()
    free_packs = ma.String()
    cards = ma.Nested(CardSchema, many=True, attribute = 'active_cards')
    high_command = ma.Nested(HighCommandSchema)

class CoachLeaderboardSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "short_name","collection_value", "earned", "bb2_name")

class SimpleCoachSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "short_name", "disc_id", "web_admin", "super_admin", "bb2_name")

class DeckSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Deck
        include_relationships = True
    
    extra_cards = ma.Nested(CardSchema, many=True)
    unused_extra_cards = ma.Nested(CardSchema, many=True)
    starter_cards = ma.Nested(CardSchema, many=True)
    cards = ma.Nested(CardSchema, many=True)
    injury_map = ma.Dict()
    deck_upgrade_cards = ma.Nested(CardSchema, many=True)
    disabled_cards = ma.List(ma.String)
    squad = ma.Nested(HighCommandSquadSchema, many=False)

class CrackerCardTemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CrackerCardTemplate
        exclude = ["cards"]
        include_relationships = True
    cyanide_player_type = ma.String()

class CrackerCardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CrackerCard
        include_relationships = True
    
    cracker_template = ma.Nested(CrackerCardTemplateSchema)
    coach = ma.String()

cards_schema = CardSchema(many=True)
cracker_cards_schema = CrackerCardSchema(many=True)
card_schema = CardSchema()
coach_schema = CoachSchema()
leaderboard_coach_schema = CoachLeaderboardSchema(many=True)
coaches_schema = SimpleCoachSchema(many=True)
tournaments_schema = TournamentSchema(many=True)
tournament_schema = TournamentSchema()
duster_schema = DusterSchema()
deck_schema = DeckSchema()
high_command_schema = HighCommandSchema()
