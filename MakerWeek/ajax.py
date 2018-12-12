import binascii
import datetime
import os
import copy

from flask import Blueprint, g, request, json, redirect, url_for
from peewee import DoesNotExist, fn, SQL

from MakerWeek.async_ops import deleteClient, exportClient, sendSMSVerify
from MakerWeek.common import checkPassword, hashPassword, paramsParse, timeSubtract, fromTimestamp, verifyPhoneNumber
from MakerWeek.config import Config
from MakerWeek.database.database import Client, LastEvent, Event, TagsMap, Tags, User, PhoneVerification

config = Config()

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
    subscriber_list = copy.copy(client.subscriber_list)
    subscriber_list.remove(userID)
    client.subscriber_list = subscriber_list
    client.save()
    return json.jsonify(result="success")


@ajax.route("/user_settings/save_general", methods=["POST"])
def saveGeneralSettings():
    if g.user is None:
        redirect("/login?needToLogin")
    g.user.email = request.form['email']
    g.user.realname = request.form['realname']
    avatarURI = request.form['avatar']
    if not avatarURI.startswith("data:image/jpeg;base64,"):
        return json.jsonify(result="invalid avatar"), 400
    with open(os.path.join(config.AVATAR_FOLDER, g.user.username + ".jpg"), "wb") as f:
        f.write(binascii.a2b_base64(avatarURI[23:]))
    g.user.avatar = g.user.username + ".jpg"
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
        "private": "bool",

        "temperature_limit": "float",
        "humidity_limit": "float",
        "colevel_limit": "float",
        "dustlevel_limit": "float"
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
    client.temperature_limit = params['temperature_limit']
    client.humidity_limit = params['humidity_limit']
    client.colevel_limit = params['colevel_limit']
    client.dustlevel_limit = params['dustlevel_limit']
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
def exportClientRoute():
    if g.user is None:
        return json.jsonify(result="Need to login")
    clientID = request.args['clientID']
    client = Client.get(Client.id == clientID)
    if client.owner != g.user:
        return json.jsonify(result="you don't have permission"), 403
    exportClient(clientID, request.args['format'], request.args['compression'])
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


def getMinEventTimestamp(clientID):
    query = (Event
             .select(fn.MIN(Event.timestamp).alias("timestamp"))
             .where((Event.client_id == clientID))
             .get())
    return query.timestamp.timestamp()


@ajax.route("/get/client_data_range")
def getEventRange():
    # asumming 5 min interval
    clientID = request.args['clientID']
    rangeFrom = int(request.args['from'])
    if rangeFrom == -1:
        rangeFrom = getMinEventTimestamp(clientID)
    rangeTo = int(request.args['to'])
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
    return json.jsonify([event.toFrontendObject(include_id=False) for event in events])


@ajax.route("/tags/top5")
def tagsTop5():
    raw = (Tags
           .select(Tags.title, Tags.description)
           .join(TagsMap)
           .group_by(Tags.id)
           .order_by(fn.COUNT(TagsMap.client_id))
           .limit(5))
    result = []
    for q in raw:
        result.append({"title": q.title, "description": q.description})
    return json.jsonify(result)


@ajax.route("/tags/suggest")
def tagsSuggest():
    query = request.args['q']
    words = query.split(" ")
    words[-1] += '*'
    query = " ".join(words)
    raw = (Tags
           .select(Tags.title, Tags.description)
           .join(TagsMap)
           .where(SQL("MATCH(title) AGAINST(%s IN BOOLEAN MODE)", (query,)))
           .group_by(Tags.id)
           .order_by(fn.COUNT(TagsMap.client_id))
           .limit(5))

    result = []
    for q in raw:
        result.append({"title": q.title, "description": q.description})
    return json.jsonify(result)


@ajax.route("/tags/list_clients")
def tagsListClients():
    title = request.args['title']
    if 'page' not in request.args:
        page = 1
    else:
        page = int(request.args['page'])
    query = (LastEvent
             .select(LastEvent, Client)
             .join(Event)
             .join(Client)
             .join(TagsMap)
             .join(Tags)
             .where(Tags.title == title)
             .paginate(page, 10))
    if g.user is None:
        query = (query
                 .where(~Client.private))
    else:
        query = (query
                 .where(~Client.private | (Client.private & Client.owner == g.user)))
    return json.jsonify(
        [q.event_id.toFrontendObject(include_id=True, include_geo=True, include_owner=True) for q in query])


@ajax.route("/search")
def navbarSearch():
    type = request.args['type']
    keywords = request.args['q']
    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1
    if type == "Tags":
        query = (Tags
                 .select(Tags.title, Tags.description, fn.COUNT(SQL("client_id_id")).alias("count"))
                 .join(TagsMap)
                 .where(SQL("MATCH(title) AGAINST(%s IN BOOLEAN MODE)", (keywords,))
                        | SQL("MATCH(description) AGAINST(%s IN BOOLEAN MODE)", (keywords,)))
                 .group_by(TagsMap.tag_id)
                 .paginate(page, 12)
                 .dicts())
        return json.jsonify([{
                                 "title": tag['title'],
                                 "description": tag['description'],
                                 "count": tag['count']
                             } for tag in query])
    elif type == "Users":
        query = (User
                 .select()
                 .where(SQL("MATCH(username) AGAINST(%s IN BOOLEAN MODE)", (keywords,))
                        | SQL("MATCH(realname) AGAINST(%s IN BOOLEAN MODE)", (keywords,)))
                 .paginate(page, 10))
        return json.jsonify([{
                                 "username": user.username,
                                 "realname": user.realname,
                                 "avatar": url_for("static", filename=os.path.join("avatar", user.avatar))} for user in
                             query])
    elif type == "Clients":
        tags = []
        names = []
        for keyword in keywords.split(" "):
            if keyword.startswith("tags:"):
                tags.append(keyword[5:])
            else:
                names.append(keyword)
        names[-1] += '*'

        query = (LastEvent
                 .select(LastEvent, Client, User, TagsMap, Tags)
                 .join(Client, on=(LastEvent.client_id == Client.id))
                 .join(User, on=(Client.owner == User.id))
                 .join(TagsMap, on=(TagsMap.client_id == Client.id))
                 .join(Tags, on=(Tags.id == TagsMap.tag_id))
                 .where(SQL("MATCH(name) AGAINST(%s IN BOOLEAN MODE)", (" ".join(names),)))
                 .group_by(Client.id))
        if len(tags) != 0:
            query = (query
                     .where(SQL("MATCH(title) AGAINST(%s IN BOOLEAN MODE)", (" ".join(tags),))))
        if g.user is None:
            query = (query
                     .where(~Client.private))
        else:
            query = (query
                     .where(~Client.private | (Client.private & (Client.owner == g.user))))
        query = query.paginate(page, 10)
        return json.jsonify(
            [q.event_id.toFrontendObject(include_id=True, include_geo=True, include_owner=True) for q in query])


@ajax.route("/initiatePhoneVerification")
def initiatePhoneVerification():
    if g.user is None:
        return json.jsonify(result="need to login")
    phone = request.args['phone']
    if not verifyPhoneNumber(phone):
        return json.jsonify(result="invalid number")
    try:
        obj = PhoneVerification.get((PhoneVerification.user_id == g.user) & (PhoneVerification.phone == phone))
    except DoesNotExist:
        pass
    else:
        obj.delete_instance()
    finally:
        obj = PhoneVerification.create(phone=phone, user_id=g.user)
    sendSMSVerify(phone, obj.verifyCode)
    return json.jsonify(result="success")


@ajax.route("/resendPhoneVerification")
def resendPhoneVerification():
    if g.user is None:
        return json.jsonify(result="need to login")
    phone = request.args['phone']
    if not verifyPhoneNumber(phone):
        return json.jsonify(result="invalid number")
    try:
        obj = PhoneVerification.get((PhoneVerification.user_id == g.user) & (PhoneVerification.phone == phone))
    except DoesNotExist:
        return json.jsonify(result="not found")
    sendSMSVerify(phone, obj.verifyCode)
    return json.jsonify(result="success")


@ajax.route("/answerPhoneVerification")
def answerPhoneVerification():
    if g.user is None:
        return json.jsonify(result="need to login")
    phone = request.args['phone']
    try:
        obj = PhoneVerification.get((PhoneVerification.user_id == g.user) & (PhoneVerification.phone == phone))
    except DoesNotExist:
        return json.jsonify(result="not found")
    if timeSubtract(hours=1) > obj.timestamp.replace(tzinfo=datetime.timezone.utc):
        obj.delete_instance()
        return json.jsonify(result="timeout")
    if obj.tryCount >= 5:
        obj.delete_instance()
        return json.jsonify(result="too many attempts")
    if str(obj.verifyCode) != request.args['verifyCode']:
        obj.tryCount += 1
        obj.save()
        return json.jsonify(result="wrong code")
    obj.user_id.phone = obj.phone
    obj.user_id.save()
    obj.delete_instance()
    return json.jsonify(result="success")


@ajax.route("/get/user_clients")
def getUserClients():
    username = request.args['username']
    try:
        page = int(request.args['page'])
    except Exception:
        page = 1
    try:
        user = User.get(User.username == username)
    except DoesNotExist:
        return "user not found", 404
    query = (LastEvent
             .select(LastEvent, Client, User)
             .join(Client, on=(LastEvent.client_id == Client.id))
             .join(User, on=(Client.owner == User.id))
             .where(Client.owner == user)
             .paginate(page, 10))
    if (g.user is None) or (g.user != user):
        query = (query
                 .where(~Client.private))
    return json.jsonify(
        [q.event_id.toFrontendObject(include_id=True, include_geo=True, include_owner=True) for q in query])
