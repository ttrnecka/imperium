from flask_marshmallow import Marshmallow
from .data_models import Transaction, Account, Card, Coach, Tournament, TournamentSignups, Duster

ma = Marshmallow()

class TransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

class AccountSchema(ma.ModelSchema):
    class Meta:
        model = Account
    transactions = ma.Nested(TransactionSchema, many=True)

class CardSchema(ma.ModelSchema):
    class Meta:
        model = Card

class TournamentSignupSchema(ma.ModelSchema):
    class Meta:
        model = TournamentSignups

class TournamentSchema(ma.ModelSchema):
    class Meta:
        model = Tournament
        exclude = ["coaches"]
    tournament_signups = ma.Nested(TournamentSignupSchema, many=True)

class DusterSchema(ma.ModelSchema):
    class Meta:
        model = Duster

class CoachSchema(ma.ModelSchema):
    class Meta:
        model = Coach
    
    cards = ma.Nested(CardSchema, many=True)
    account = ma.Nested(AccountSchema)
    duster = ma.Nested(DusterSchema)
    short_name = ma.String()

class SimpleCoachSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "short_name","disc_id","web_admin")

cards_schema = CardSchema(many=True)
coach_schema = CoachSchema()
coaches_schema = SimpleCoachSchema(many=True)
tournaments_schema = TournamentSchema(many=True)
tournament_schema = TournamentSchema()
duster_schema = DusterSchema()
