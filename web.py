import os
from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from misc.helpers import CardHelper
#from imperiumbase import Coach, Pack
from models.base_model import db
from models.data_models import Coach, Card, Account, Transaction
from services import PackService
from flask_marshmallow import Marshmallow

os.environ["YOURAPPLICATION_SETTINGS"] = "config/config.py"

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    db.init_app(app)
    return app

app = create_app()
migrate = Migrate(app, db)
ma = Marshmallow(app)

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

card_schema = CardSchema()
cards_schema = CardSchema(many=True)

class CoachSchema(ma.ModelSchema):
    class Meta:
        model = Coach
    
    cards = ma.Nested(CardSchema, many=True)
    account = ma.Nested(AccountSchema)
    short_name = ma.String()

coach_schema = CoachSchema()
coaches_schema = CoachSchema(many=True)

@app.route("/")
def index():
    starter_cards = PackService.generate("starter").cards
    return render_template("index.html",starter_cards=starter_cards)

@app.route("/coaches", methods=["GET"])
def get_coaches():
    all_coaches = Coach.query.all()
    result = coaches_schema.dump(all_coaches)
    return jsonify(result.data)

@app.route("/cards/starter", methods=["GET"])
def get_starter_cards():
    starter_cards = PackService.generate("starter").cards
    result = cards_schema.dump(starter_cards)
    return jsonify(result.data)

# run the application
if __name__ == "__main__":
    app.run()
