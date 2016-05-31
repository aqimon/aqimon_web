from MakerWeek.api import api
from MakerWeek.realtime import realtimeServer
from MakerWeek.authentication import authentication
from flask import Flask, render_template

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(authentication)
realtimeServer.init_app(app)
app.secret_key="xxx"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/client/<clientID>")
def client(clientID):
    return render_template("client.html", clientID=clientID)