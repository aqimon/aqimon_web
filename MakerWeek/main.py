from flask import Flask, render_template, session, g, request

from MakerWeek.ajax import ajax
from MakerWeek.api import api
from MakerWeek.authentication import authentication
from MakerWeek.config import Config
from MakerWeek.database.database import database, Client, LoginToken, InvalidToken, WebsocketToken, User
from MakerWeek.realtime import realtimeServer
from MakerWeek.user import user

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(authentication)
app.register_blueprint(user)
app.register_blueprint(ajax)
app.config.from_object(Config)
realtimeServer.init_app(app)


@app.before_request
def checkLogin():
    if ('tokenKey' not in session) or ('tokenValue' not in session) or ('wsTokenKey' not in session) or (
                'wsTokenValue' not in session):
        g.user = None
        session['previous'] = request.path
    else:
        try:
            g.user = LoginToken.use(session['tokenKey'], session['tokenValue'])
            wsUser = WebsocketToken.use(session['wsTokenKey'], session['wsTokenValue'])
        except (InvalidToken):
            User.logout()
            session['previous'] = request.path
            return
        if wsUser != g.user:
            User.logout()
            session['previous'] = request.path
            return
        g.wsTokenKey = session['wsTokenKey']
        g.wsTokenValue = session['wsTokenValue']


@app.before_request
def initDatabase():
    g.hasdb = True
    database.connect()


@app.teardown_request
def deinitDatabase(_):
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
    client = Client.get(Client.id == clientID)
    if client.private:
        if client.owner != g.user:
            return "nothing here", 403
    return render_template("client.html", client=client.toFrontendObject())


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/tags/<tagTitle>")
def tagPage(tagTitle):
    return render_template("tags.html", tagTitle=tagTitle)
