from flask import Blueprint, render_template, request, redirect, session, g
from MakerWeek.authentication import user
authentication = Blueprint("authentication", __name__, url_prefix="")

def isLoggedIn():
    return getattr(g, "user", None) is not None

@authentication.route("/login", methods=["GET"])
def loginPage():
    if isLoggedIn():
        return redirect("/", code=200)
    return render_template("login.html", user=g.user)


@authentication.route("/login", methods=["POST"])
def login():
    if isLoggedIn():
        return redirect("/", code=200)
    username = request.form['username']
    password = request.form['password']
    try:
        cookie=user.login(username, password)
    except user.LoginFailed:
        return redirect("/login?failure=1", code=401)
    else:
        session['tokenKey'], session['tokenHash']=cookie
    return redirect("/", code=200)


@authentication.route("/register", methods=["GET"])
def registerPage():
    if isLoggedIn():
        return redirect("/", code=200)
    return render_template("register.html", user=g.user)


@authentication.route("/register", methods=["POST"])
def register():
    if isLoggedIn():
        return redirect("/", code=200)
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    email=request.form['email']
    user.createNewUser(username, password, email)
    return redirect("/login?created=1", code=200)

@authentication.route("/signout")
def signOut():
    session.clear()
    return redirect("/", code=200)