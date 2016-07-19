from flask import Blueprint, g, request, json, redirect
from peewee import DoesNotExist

from MakerWeek.async import deleteClient, exportClient
from MakerWeek.common import checkPassword, hashPassword, paramsParse
from MakerWeek.database.database import Client

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
        return json.jsonify(result="Need to login")
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
    if client.owner != g.user:
        return json.jsonify(result="you don't have permission"), 403
    client.name = params['name']
    client.latitude = params['latitude']
    client.longitude = params['longitude']
    client.address = params['address']
    client.save()
    return json.jsonify(result="success")


@ajax.route("/delete/client")
def delClient():
    if g.user is None:
        return json.jsonify(result="Need to login")
    clientID = request.args['clientID']
    client = Client.get(Client.id == clientID)
    if client.owner != g.user:
        return json.jsonify(result="you don't have permission"), 403
    deleteClient(clientID)
    return json.jsonify(result="success")


@ajax.route("/export/client")
def exportClient():
    if g.user is None:
        return json.jsonify(result="Need to login")
    clientID = request.args['clientID']
    client = Client.get(Client.id == clientID)
    if client.owner != g.user:
        return json.jsonify(result="you don't have permission"), 403
    exportClient(clientID)
    return json.jsonify(result="success")


@ajax.route("/export/user")
def exportUser():
    if g.user is None:
        return json.jsonify(result="Need to login")
    clientID = request.args['clientID']
    client = Client.get(Client.id == clientID)
    if client.owner != g.user:
        return json.jsonify(result="you don't have permission"), 403
    # exportClient(clientID)
    return json.jsonify(result="success")
