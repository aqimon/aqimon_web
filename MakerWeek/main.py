from MakerWeek.api import api
from MakerWeek.realtime import realtimeServer
from flask import Flask, render_template

app = Flask(__name__)
app.register_blueprint(api)
realtimeServer.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html")