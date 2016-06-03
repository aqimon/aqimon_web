from flask import Blueprint, render_template, request, redirect, session, g, url_for
from MakerWeek.authentication import user
from MakerWeek.mail import mail

authentication = Blueprint("authentication", __name__, url_prefix="")


def isLoggedIn():
    return getattr(g, "user", None) is not None


@authentication.route("/login", methods=["GET"])
def loginPage():
    if isLoggedIn():
        return redirect("/")
    return render_template("authentication/login.html")


@authentication.route("/login", methods=["POST"])
def login():
    if isLoggedIn():
        return redirect("/")
    username = request.form['username']
    password = request.form['password']
    try:
        cookie = user.login(username, password)
    except user.LoginFailed:
        return redirect("/login?failure=1")
    else:
        session['tokenKey'], session['tokenHash'] = cookie
    return redirect("/")


@authentication.route("/register", methods=["GET"])
def registerPage():
    if isLoggedIn():
        return redirect("/")
    return render_template("authentication/register.html")


@authentication.route("/register", methods=["POST"])
def register():
    if isLoggedIn():
        return redirect("/")
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user.createNewUser(username, password, email)
    return redirect("/login?created=1")


@authentication.route("/signout")
def signOut():
    session.clear()
    return redirect("/")


@authentication.route("/forgot", methods=["GET"])
def forgotPage():
    if isLoggedIn():
        return redirect("/")
    return render_template("authentication/forgot.html")


@authentication.route("/forgot", methods=["POST"])
def resetPassword():
    email = request.form['email']
    try:
        newPassword = user.resetPassword(email)
    except user.UserNotFound:
        return redirect("/forgot?failure=1")
    mail.sendEmail(email, "Your new password", "Your new password is {}".format(newPassword))
    return redirect("/login?reset=1")
