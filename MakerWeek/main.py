from flask import Flask, render_template, session, g

from MakerWeek.ajax import ajax
from MakerWeek.api import api
from MakerWeek.authentication import authentication, loginToken
from MakerWeek.database.database import database, User, Client
from MakerWeek.realtime import realtimeServer
from MakerWeek.user import user as userBlueprint

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(authentication)
app.register_blueprint(userBlueprint)
app.register_blueprint(ajax)
realtimeServer.init_app(app)
app.secret_key = "xxx"


@app.before_request
def checkLogin():
    if ('tokenKey' not in session) or ('tokenHash' not in session):
        g.user = None
    else:
        try:
            userID = LoginToken.get(session['tokenKey'], session['tokenHash'])
        except (loginToken.LoginTokenNotCorrect, loginToken.LoginTokenNotCorrect):
            g.user = None
        else:
            g.user = User.get(User.id == userID)


@app.before_request
def initDatabase():
    database.connect()


@app.teardown_appcontext
def deinitDatabase():
    database.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/client/<clientID>")
def client(clientID):
    return render_template("client.html", client=Client.get(Client.id == clientID))
