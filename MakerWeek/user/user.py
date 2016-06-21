from flask import Blueprint, render_template, g, redirect

user = Blueprint("user", __name__, url_prefix="")


@user.before_request
def isLoggedIn():
    if g.user is None:
        return redirect("/login?needToLogin")


@user.route("/myaccount")
def myAccount():
    return render_template("user/dashboard.html")


@user.route("/myaccount/settings")
def userSettings():
    return render_template("/user/settings.html")
