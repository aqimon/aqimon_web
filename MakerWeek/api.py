import json

from flask import request, json, Blueprint

from MakerWeek.async import sendNotification
from MakerWeek.common import paramsParse, overThreshold
from MakerWeek.database.database import Client, User, Event, ForgotToken, LoginToken, database
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
        "id": "str",
        "temperature": "float",
        "humidity": "float",
        "dustlevel": "float",
        "colevel": "float"
    }
    params = paramsParse(__paramsList__, request.args)

    event = Event(**params)
    client = Client.get(Client.id == params['id'])
    client.last_event = event.id
    broadcastEvent(event.toFrontendObject())
    if overThreshold(event.colevel, event.dustlevel):
        sendNotification(event.client_id)
    return json.jsonify(result="success")


@api.route("/debug/burn")
def burn():
    database.create_table([Client, User, ForgotToken, LoginToken, Event])
    return json.jsonify(result="success")
