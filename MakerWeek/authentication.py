from flask import Blueprint, render_template, request, redirect, session, g, json
from peewee import DoesNotExist

from MakerWeek import async_queue
from MakerWeek.common import hashPassword, timeSubtract, genRandomString
from MakerWeek.database.database import User, ForgotToken, database, IncorrectPassword

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
    phone = request.form['phone']
    User.add(username, password, email, phone)
    return redirect("/login?created")


@authentication.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    try:
        session['tokenKey'], session['tokenValue'] = User.get(User.username == username).login(password)
    except (DoesNotExist, IncorrectPassword):
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
    try:
        user = User.get(User.email == email)
    except DoesNotExist:
        return json.jsonify(result="not found")
    ft_obj = ForgotToken.new(user_id=user.id)
    mailContent = render_template("authentication/forgotEmail.html",
                                  token=ft_obj.token,
                                  expiration=ft_obj.timestamp.isoformat())
    async_queue.sendMail(email, "MakerWeek reset your password", mailContent)
    return json.jsonify(result="success")


@authentication.route("/forgot2/<token>", methods=["GET"])
def resetPassword2(token):
    with database.atomic() as tx:
        try:
            token_obj = ForgotToken.get((ForgotToken.token == token) & (ForgotToken.timestamp >= timeSubtract(days=1)))
        except DoesNotExist:
            return redirect("/login?invalidToken")
        user = token_obj.user_id
        newPassword = genRandomString(20)
        user.password = hashPassword(newPassword)
        user.save()
        token_obj.delete_instance()
    mailContent = render_template("authentication/forgot2Email.html",
                                  newPassword=newPassword)
    async_queue.sendMail(user.email, "New password", mailContent)
    return redirect("/login?resetSuccess")
