from flask import Blueprint, render_template, request, redirect, session, g, json

from MakerWeek import async
from MakerWeek.database.database import User, ForgotToken

authentication = Blueprint("authentication", __name__, url_prefix="")


@authentication.before_request
def isLoggedIn():
    if getattr(g, "user", None) is not None and request.path != "/signout":
        return redirect("/")


@authentication.route("/login", methods=["GET"])
def loginPage():
    return render_template("authentication/login.html")


@authentication.route("/register", methods=["GET"])
def registerPage():
    return render_template("authentication/register.html")


@authentication.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user = User.add(username, password, email)
    return redirect("/login?created")


@authentication.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    try:
        session['tokenKey'], session['tokenValue'] = User.get(User.username == username).login(password)
    except Exception:
        return redirect("/login?failure")
    return redirect(request.form['from'])


@authentication.route("/signout")
def signOut():
    User.logout()
    return redirect("/")


@authentication.route("/forgot", methods=["GET"])
def forgotPage():
    return render_template("authentication/forgot.html")


@authentication.route("/forgot", methods=["POST"])
def resetPassword():
    email = request.form['email']
    # TODO: Exception
    user = User.get(User.email == email)
    token, time = forgotToken.generateForgotToken(userID)
    mailContent = render_template("authentication/forgotEmail.html", token=token, expiration=time.isoformat())
    async.sendMail(email, "MakerWeek reset your password", mailContent)
    return json.jsonify(result="success")


@authentication.route("/forgot_with_token/<token>", methods=["GET"])
def resetPassword2(token):
    # TODO: exception when token is not valid
    token_obj = ForgotToken.get(ForgotToken.token == token)
    # TODO: Render mail from HTML
    mailContent = """
        Your new temporary password is: {}. Please sign in using this temporary password and then change it immediately.
    """.format(newPassword)
    async.sendMail(user.getEmailFromID(userID), "New password", mailContent)
    return redirect("/login?resetSuccess")


@authentication.route("/forgot_after_token")
