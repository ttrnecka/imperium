
from flask import Flask, render_template
from imperiumbase import Coach, Pack

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    sorted_coached = sorted(Coach.all(), key=lambda x: x.name)
    return render_template("index.html", coaches = sorted_coached, Pack = Pack)

# run the application
if __name__ == "__main__":  
    app.run(debug=True)
