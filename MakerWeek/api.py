import json

from flask import request, json, Blueprint
from peewee import DoesNotExist

from MakerWeek.async import sendNotification
from MakerWeek.common import paramsParse, overThreshold, timeSubtract, utcNow, fromTimestamp
from MakerWeek.database.database import Client, User, Event, ForgotToken, LoginToken, database, LastEvent
from MakerWeek.realtime import broadcastEvent

api = Blueprint('api', __name__, url_prefix="/api")


@api.route("/get/client")
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
    if 'time' not in request.args:
        time = utcNow()
    else:
        time = fromTimestamp(request.args['time'])
    params = paramsParse(__paramsList__, request.args)
    with database.atomic() as tx:
        try:
            client = Client.get(Client.id == params['client_id'])
        except DoesNotExist:
            return json.jsonify(result="no such client"), 404
        if client.api_key != params['apikey']:
            return json.jsonify(result="invalid api key"), 403
        del params['apikey']
        event = Event.create(**params, timestamp=time)
        event.save()
        last_event, created = LastEvent.create_or_get(client_id=event.client_id, event_id=event.id)
        last_event.event_id = event.id
        last_event.save()

    broadcastEvent(event.toFrontendObject(include_geo=True))
    if overThreshold(event.colevel, event.dustlevel):
        sendNotification(str(event.client_id.id))
    return json.jsonify(result="success")


@api.route("/debug/burn")
def burn():
    database.create_tables([User, Client, Event, ForgotToken, LoginToken, LastEvent], safe=False)
    return json.jsonify(result="success")