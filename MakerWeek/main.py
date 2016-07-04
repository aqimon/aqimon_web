from flask import Flask, render_template, session, g
from peewee import DoesNotExist

from MakerWeek.ajax import ajax
from MakerWeek.api import api
from MakerWeek.authentication import authentication
from MakerWeek.common import genRandomString
from MakerWeek.database.database import database, User, Client, LoginToken, InvalidToken
from MakerWeek.realtime import realtimeServer
from MakerWeek.user import user

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(authentication)
app.register_blueprint(user)
app.register_blueprint(ajax)
realtimeServer.init_app(app)
app.secret_key = genRandomString(512)

@app.before_request
def checkLogin():
    if ('tokenKey' not in session) or ('tokenValue' not in session):
        g.user = None
    else:
        try:
            userID = LoginToken.use(session['tokenKey'], session['tokenValue'])
        except (InvalidToken):
            g.user = None
            return
        try:
            g.user = User.get(User.id == userID)
        except DoesNotExist:
            g.user = None


@app.before_request
def initDatabase():
    g.hasdb = True
    database.connect()


@app.teardown_request
def deinitDatabase(args):
    if 'hasdb' in g:
        database.close()
        del g.hasdb


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/client/<clientID>")
def client(clientID):
    return render_template("client.html", client=Client.get(Client.id == clientID))
