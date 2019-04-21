import os
from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from misc.helpers import CardHelper
#from imperiumbase import Coach, Pack
from models.base_model import db
from models.data_models import Coach
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


class CoachSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('name', 'short_name')


coach_schema = CoachSchema()
coaches_schema = CoachSchema(many=True)

@app.route("/")
def index():
    starter_cards = PackService.generate("starter").cards
    sorted_coached = Coach.query.order_by(Coach.name).all()
    return render_template("index.html", coaches = sorted_coached, ch=CardHelper, starter_cards=starter_cards)

@app.route("/coach", methods=["GET"])
def get_coach():
    all_coaches = Coach.query.all()
    result = coaches_schema.dump(all_coaches)
    return jsonify(result.data)

# run the application
if __name__ == "__main__":
    app.run()
