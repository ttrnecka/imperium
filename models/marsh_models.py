from flask_marshmallow import Marshmallow
from .data_models import Transaction, Account, Card, Coach, Tournament, TournamentSignups, Duster, Deck, CrackerCard, CrackerCardTemplate
from .data_models import CardTemplate

ma = Marshmallow()

class TransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

class AccountSchema(ma.ModelSchema):
    class Meta:
        model = Account
    #transactions = ma.Nested(TransactionSchema, many=True)
    transactions = ma.Nested(TransactionSchema, many=True, attribute = 'last_transactions')

class CardTemplateSchema(ma.ModelSchema):
    class Meta:
        model = CardTemplate
        exclude = ["cards"]
    date_modified = ma.String()
    date_created = ma.String()

class CardSchema(ma.ModelSchema):
    class Meta:
        model = Card
        exclude = ["decks", "coach"]
    assigned_to_array = ma.Dict(ma.List(ma.String))
    template = ma.Nested(CardTemplateSchema)
    default_skills = ma.List(ma.String())
    coach_data = ma.Dict(attribute = 'coach_dict')

class TournamentSignupSchema(ma.ModelSchema):
    class Meta:
        model = TournamentSignups
    coach = ma.Integer(attribute = 'coach_id')
    deck = ma.Integer(attribute = 'deck_id')

class TournamentSchema(ma.ModelSchema):
    class Meta:
        model = Tournament
        exclude = ["coaches","conclave_triggers"]
    tournament_signups = ma.Nested(TournamentSignupSchema, many=True)

class DusterSchema(ma.ModelSchema):
    class Meta:
        model = Duster

class CoachSchema(ma.ModelSchema):
    class Meta:
        model = Coach
        exclude = ["packs"]
    
    account = ma.Nested(AccountSchema)
    duster = ma.Nested(DusterSchema)
    short_name = ma.String()
    achievements = ma.Dict()
    stats = ma.Dict()
    free_packs = ma.String()
    cards = ma.Nested(CardSchema, many=True, attribute = 'active_cards')

class CoachLeaderboardSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "short_name","collection_value", "earned", "bb2_name")

class SimpleCoachSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "short_name", "disc_id", "web_admin", "bb2_name")

class DeckSchema(ma.ModelSchema):
    class Meta:
        model = Deck
    
    extra_cards = ma.Nested(CardSchema, many=True)
    unused_extra_cards = ma.Nested(CardSchema, many=True)
    starter_cards = ma.Nested(CardSchema, many=True)
    cards = ma.Nested(CardSchema, many=True)
    injury_map = ma.Dict()
    deck_upgrade_cards = ma.Nested(CardSchema, many=True)
    disabled_cards = ma.List(ma.String)

class CrackerCardTemplateSchema(ma.ModelSchema):
    class Meta:
        model = CrackerCardTemplate
        exclude = ["cards"]
    cyanide_player_type = ma.String()

class CrackerCardSchema(ma.ModelSchema):
    class Meta:
        model = CrackerCard
    
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
