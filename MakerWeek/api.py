import json

from flask import request, json, Blueprint

from MakerWeek.async import sendNotification
from MakerWeek.common import paramsParse, overThreshold
from MakerWeek.database.database import Client, User, Event, ForgotToken, LoginToken, database, LastEvent
from MakerWeek.realtime import broadcastEvent

api = Blueprint('api', __name__, url_prefix="/api")


@api.route("/add/event")
def addEvent():
    # API: Add events from a client
    # Parameters:
    #  - clientID: client id
    #  - temperature, humidity, dustLevel, coLevel: self-explanatory
    #  TODO: - apiKey: API key specific to that client
    # Returns:
    #  {"result": <result>}

    __paramsList__ = {
        "client_id": "str",
        "temperature": "float",
        "humidity": "float",
        "dustlevel": "float",
        "colevel": "float"
    }
    params = paramsParse(__paramsList__, request.args)

    with database.atomic() as tx:
        event = Event.create(**params)
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