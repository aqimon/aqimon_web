import json

from flask import Blueprint, render_template, request, redirect, session, g

from MakerWeek.authentication import user, forgotToken
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
        return redirect("/login?failure")
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
    return redirect("/login?created")


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
        userID = user.getIDFromEmail(email)
    except user.UserNotFound:
        return json.dumps({"result": "UserNotFound"})
    token, time = forgotToken.generateForgotToken(userID)
    mailContent = render_template("authentication/forgotEmail.html", token=token, expiration=time.isoformat())
    mail.sendEmail(email, "MakerWeek reset your password", mailContent)
    return json.dumps({"result": "success"})


@authentication.route("/forgot2/<token>", methods=["GET"])
def resetPassword2(token):
    try:
        userID = forgotToken.useForgotToken(token)
    except (forgotToken.TokenExpired, forgotToken.TokenExpired):
        return redirect("/login.html?invalidToken")
    newPassword = user.resetPassword(userID)
    mailContent = """
        Your new temporary password is: {}. Please sign in using this temporary password and then change it immediately.
    """.format(newPassword)
    mail.sendEmail(user.getEmailFromID(userID), "New password", mailContent)
    return redirect("/login?resetSuccess")
