from flask import Flask, render_template
#from imperiumbase import Coach, Pack
from models.base_model import db
from models.data_models import Coach

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    #app.config.from_pyfile(config_filename)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/db/imperium.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

@app.route("/")
def index():
    sorted_coached = sorted(Coach.query.all(), key=lambda x: x.name)
    return render_template("index.html", coaches = sorted_coached)

# run the application
if __name__ == "__main__":  
    app.run(debug=True)
