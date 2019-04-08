from flask_sqlalchemy import SQLAlchemy
from sqlathanor import FlaskBaseModel, initialize_flask_sqlathanor

db = SQLAlchemy(model_class = FlaskBaseModel)
db = initialize_flask_sqlathanor(db)

class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
