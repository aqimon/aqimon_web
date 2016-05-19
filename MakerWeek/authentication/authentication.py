from flask import Blueprint, render_template

authentication = Blueprint("authentication", __name__, url_prefix="")


@authentication.route("/login", methods=["GET"])
def loginPage():
    return render_template("login.html")


@authentication.route("/login", methods=["POST"])
def login():
    pass


@authentication.route("/register", methods=["GET"])
def registerPage():
    return render_template("register.html")


@authentication.route("/register", methods=["POST"])
def register():
    pass
