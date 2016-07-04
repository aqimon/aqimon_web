from flask import Blueprint, g, request, json, redirect
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
    client.save()
    return json.jsonify(result="success")


@ajax.route("/notification/unsubscribe")
def unsubscribe():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.get(Client.id == clientID)
    client.subscriber_list.remove(userID)
    client.save()
    return json.jsonify(result="success")


@ajax.route("/get/client")
def getClientInfo():
    clientID = request.args['clientID']
    includeEvents = 'includeEvents' in request.args
    try:
        client = Client.get(Client.id == clientID)
    except DoesNotExist:
        return json.jsonify({"msg": "no such client"}), 404
    response = {
        "clientID": client.id,
        "name": client.name,
        "latitude": client.latitude,
        "longitude": client.longitude,
        "address": client.address,
        "owner": client.owner.id
    }
    if includeEvents:
        events = (Event
                  .select(Event, Client)
                  .join(Client)
                  .where((Event.client_id == client.id) & (Event.timestamp >= timeSubtract(days=1))))
        response.update({
            "events": [event.toFrontendObject(include_id=False) for event in events]
        })
    return json.jsonify(**response)


@ajax.route("/user_settings/save_general")
def saveGeneralSettings():
    if g.user is None:
        redirect("/login?needToLogin")
    newUsername = request.args['username']
    newEmail = request.args['email']
    newPhone = request.args['phone']
    g.user.username = newUsername
    g.user.email = newEmail
    g.user.phone = newPhone
    g.user.save()
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
    g.user.save()
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
    #   apiKey: API key for that client

    __paramsList__ = {
        "name": "str",
        "latitude": "float",
        "longitude": "float",
        "address": "str",
    }

    if g.user is None:
        return json.jsonify(result='need to login first')
    params = paramsParse(__paramsList__, request.args)
    params['owner'] = g.user.id
    client = Client.create(**params)
    return json.jsonify(result="success", apiKey=client.api_key, clientID=str(client.id))


@ajax.route("/edit/client")
def editClient():
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    __paramsList__ = {
        "clientID": "str",
        "name": "str",
        "latitude": "float",
        "longitude": "float",
        "address": "str",
    }
    params = paramsParse(__paramsList__, request.args)
    try:
        client = Client.get(Client.id == params['clientID'])
    except DoesNotExist:
        return json.jsonify(result="clientid not found"), 404
    client.name = params['name']
    client.latitude = params['latitude']
    client.longitude = params['longitude']
    client.address = params['address']
    client.save()
    return json.jsonify(result="success")
