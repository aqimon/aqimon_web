import json

from flask import request, json, Blueprint
from peewee import DoesNotExist

from MakerWeek.async import sendNotification
from MakerWeek.common import paramsParse, overThreshold, utcNow, fromTimestamp
from MakerWeek.database.database import Client, User, Event, ForgotToken, LoginToken, database, LastEvent, Tags, \
    TagsMap, WebsocketToken
from MakerWeek.realtime import broadcastEvent

api = Blueprint('api', __name__, url_prefix="/api")

@api.route("/add/event")
def addEvent():
    # API: Add events from a client
    # Parameters:
    #  - clientID: client id
    #  - temperature, humidity, dustLevel, coLevel: self-explanatory
    #  - apiKey: API key specific to that client
    # Returns:
    #  {"result": <result>}

    __paramsList__ = {
        "client_id": "str",
        "temperature": "float",
        "humidity": "float",
        "dustlevel": "float",
        "colevel": "float",
        "apikey": "str"
    }
    params = paramsParse(__paramsList__, request.args)
    if 'time' not in request.args:
        params['timestamp'] = utcNow()
    else:
        params['timestamp'] = fromTimestamp(request.args['time'])
    with database.atomic() as tx:
        try:
            client = Client.get(Client.id == params['client_id'])
        except DoesNotExist:
            return json.jsonify(result="no such client"), 404
        if client.api_key != params['apikey']:
            return json.jsonify(result="invalid api key"), 403
        del params['apikey']
        event = Event.create(**params)
        last_event, created = LastEvent.create_or_get(client_id=event.client_id, event_id=event.id)
        last_event.event_id = event.id
        last_event.save()

    broadcastEvent(event.toFrontendObject(include_geo=True), private=client.private)
    if overThreshold(event.colevel, event.dustlevel):
        if not client.last_notification:
            sendNotification(str(event.client_id.id), True)
            client.last_notification = True
            client.save()
    else:
        if client.last_notification:
            sendNotification(str(event.client_id.id), False)
            client.last_notification = False
            client.save()

    return json.jsonify(result="success")


@api.route("/debug/burn")
def burn():
    database.create_tables([User, Client, Event, ForgotToken, LoginToken, LastEvent, Tags, TagsMap, WebsocketToken],
                           safe=False)
    return json.jsonify(result="success")