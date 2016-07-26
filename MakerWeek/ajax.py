from flask import Blueprint, g, request, json, redirect
from peewee import DoesNotExist, fn, SQL

from MakerWeek.async import deleteClient, exportClient
from MakerWeek.common import checkPassword, hashPassword, paramsParse, timeSubtract, fromTimestamp
from MakerWeek.database.database import Client, Event, TagsMap

ajax = Blueprint('ajax', __name__, url_prefix="/ajax")


@ajax.route("/get/client")
def getClientInfo():
    clientID = request.args['clientID']
    includeEvents = 'includeEvents' in request.args
    try:
        client = Client.get(Client.id == clientID)
    except DoesNotExist:
        return json.jsonify({"msg": "no such client"}), 404
    if client.private:
        if client.owner != g.user:
            return "", 403
    response = {
        "clientID": client.id,
        "name": client.name,
        "latitude": client.latitude,
        "longitude": client.longitude,
        "address": client.address,
        "owner": client.owner.id,
        "tags": [tag.title for tag in client.getTags()],
        "private": client.private
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
        "private": "bool",
    }

    if g.user is None:
        return json.jsonify(result='need to login first')
    params = paramsParse(__paramsList__, request.args)
    params['owner'] = g.user.id
    client = Client.create(**params)
    tags = json.loads(request.args['tags'])
    TagsMap.link(client, tags)
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
        "tags": "json",
        "private": "bool"
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
    client.private = params['private']
    client.save()
    TagsMap.link(client, params['tags'])
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


@ajax.route("/get/client_data_range")
def getEventRange(clientID, rangeFrom, rangeTo):
    # asumming 5 min interval
    client = Client.get(Client.id == clientID)
    dateFrom = fromTimestamp(rangeFrom)
    dateTo = fromTimestamp(rangeTo)
    delta = dateTo - dateFrom
    if client.private and (client.owner != g.user):
        return "", 403
    if (delta.days <= 1):
        # range <= 1 day, return all
        # 288 points
        print("1 day query")
        events = (Event
                  .select()
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .order_by(Event.timestamp))
    elif (delta.days <= 3):
        # range <= 3 days, 10 minutes period
        # 432 points
        print("3 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval (MINUTE(timestamp) mod 10) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), fn.HOUR(Event.timestamp), SQL("MINUTE(timestamp) div 10"))
                  .order_by(Event.timestamp))
    elif (delta.days <= 7):
        # range <= 1 week, 20 minutes period
        # 504 points
        print("7 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval (MINUTE(timestamp) mod 20) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), fn.HOUR(Event.timestamp), SQL("MINUTE(timestamp) div 20"))
                  .order_by(Event.timestamp))
    elif (delta.days <= 30):
        # range <= 1 month, 2 hour period, average
        # 372 points per type
        print("30 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval MINUTE(timestamp) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), SQL("HOUR(timestamp) div 2"))
                  .order_by(Event.timestamp))
    else:
        print(">1 month query")
        # range >=1 month, 1 day period, average
        # min 365/366 datapoints per type
        events = (Event
                  .select(fn.DATE(Event.timestamp).alias("timestamp"),
                          fn.AVG(Event.temperature).alias("temperature"),
                          fn.AVG(Event.humidity).alias("humidity"),
                          fn.AVG(Event.dustlevel).alias("dustlevel"),
                          fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp))
                  .order_by(Event.timestamp))
    return json.jsonify(result=[event.toFrontendObject(include_id=False) for event in events])
