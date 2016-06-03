from MakerWeek.api import api
from MakerWeek.realtime import realtimeServer
from MakerWeek.authentication import authentication, loginToken, user
from flask import Flask, render_template, session, g

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(authentication)
realtimeServer.init_app(app)
app.secret_key="xxx"

@app.before_request
def checkLogin():
    if ('tokenKey' not in session) or ('tokenHash' not in session):
        g.user=None
    else:
        try:
            userID=loginToken.get(session['tokenKey'], session['tokenHash'])
        except (loginToken.LoginTokenNotCorrect, loginToken.LoginTokenNotCorrect):
            g.user=None
        else:
            g.user=user.User(userID)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/client/<clientID>")
def client(clientID):
    return render_template("client.html", clientID=clientID)