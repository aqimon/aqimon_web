from flask import Blueprint, g, request, json, redirect, Response
from peewee import DoesNotExist

from MakerWeek.common import timeSubtract, checkPassword, hashPassword, paramsParse
from MakerWeek.database.database import Client, Event

ajax = Blueprint('ajax', __name__, url_prefix="/ajax")


@ajax.route("/notification/subscribe")
def subscribe():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.get(Client.id == clientID)
    client.subscriber_list.append(userID)
    return json.jsonify(result="success")


@ajax.route("/notification/unsubscribe")
def unsubscribe():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.get(Client.id == clientID)
    client.subscriber_list.remove(userID)
    return json.jsonify(result="success")


@ajax.route("/get/client")
def getClientInfo():
    clientID = request.args['clientID']
    try:
        client = Client.get(Client.client_id == clientID)
    except DoesNotExist:
        return json.jsonify({"msg": "no such client"}), 404
    events = Event.select().where((Event.client_id == client.id) & (Event.timestamp >= timeSubtract(days=1)))
    response = {
        "id": client.id,
        "latitude": client.latitude,
        "longitude": client.longitude,
        "address": client.address,
        "owner": client.owner,
        "events": [event.toFrontendObject() for event in events]
    }
    return Response(json.dumps(response), mimetype="application/json")


@ajax.route("/user_settings/save_general")
def saveGeneralSettings():
    if g.user is None:
        redirect("/login?needToLogin")
    newUsername = request.args['username']
    newEmail = request.args['email']
    g.user.username = newUsername
    g.user.email = newEmail
    return json.jsonify(result="success")


@ajax.route("/user_settings/change_password")
def changePassword():
    if g.user is None:
        redirect("/login?needToLogin")
    oldPassword = request.args['old_password']
    if not checkPassword(g.user.password, oldPassword):
        return json.dumps({"result": "incorrect old password"})
    newPassword = request.args['new_password']
    g.user.password = hashPassword(newPassword)
    g.user.logout()
    return json.jsonify(result="success")


@ajax.route("/add/client")
def addClient():
    # AJAX: Add new client
    # Parameters:
    #  - id: Uniquely identified ID
    #  - latitude, longitude: client's location in latitude and longitude
    #  - address: client's location in real world address
    # Returns
    #   TODO: Returns API key?

    __paramsList__ = {
        "clientID": "str",
        "latitude": "float",
        "longitude": "float",
        "address": "str",
    }
    if g.user is None:
        return "{result: 'need to login first'}"
    params = paramsParse(__paramsList__, request.args)
    params['owner'] = g.user.id
    client = Client(**params)
    client.dbWrite()
    return json.dumps({"result": "success"})
