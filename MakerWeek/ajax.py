from flask import Blueprint, g, request, json, redirect
from peewee import DoesNotExist, fn, SQL

from MakerWeek.async import deleteClient, exportClient
from MakerWeek.common import checkPassword, hashPassword, paramsParse, timeSubtract, fromTimestamp
from MakerWeek.database.database import Client, LastEvent, Event, TagsMap, Tags, User

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


@ajax.route("/user_settings/save_general", methods=["POST"])
def saveGeneralSettings():
    if g.user is None:
        redirect("/login?needToLogin")
    g.user.email = request.form['email']
    g.user.phone = request.form['phone']
    g.user.realname = request.form['realname']
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
                        | SQL("MATCH(name) AGAINST(%s IN BOOLEAN MODE)", (keywords,)))
                 .paginate(page, 10))
        return json.jsonify([{
                                 "username": user.title,
                                 "name": user.name,
                                 "avatar": user.avatar} for user in query])
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
                     .where(~Client.private | (Client.private & Client.owner == g.user)))
        query = query.paginate(page, 10)
        return json.jsonify(
            [q.event_id.toFrontendObject(include_id=True, include_geo=True, include_owner=True) for q in query])
