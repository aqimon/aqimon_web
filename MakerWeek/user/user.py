from flask import Blueprint

user=Blueprint("user", __name__, url_prefix="")

@user.route("/myaccount")
def myAccount():
    pass

@user.route("/myaccount/settings")
def userSettings():
    pass