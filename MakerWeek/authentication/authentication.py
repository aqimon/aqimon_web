from flask import Blueprint, render_template, request, redirect, session, g
from MakerWeek.authentication import user
authentication = Blueprint("authentication", __name__, url_prefix="")

@authentication.route("/login", methods=["GET"])
def loginPage():
    return render_template("login.html")


@authentication.route("/login", methods=["POST"])
def login():
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
    return render_template("register.html")


@authentication.route("/register", methods=["POST"])
def register():
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    email=request.form['email']
    user.createNewUser(username, password, email)
    return redirect("/login?created=1", code=200)
