import json

from MakerWeek.common import paramsParse
from MakerWeek.database import getDB
from MakerWeek.objects.client import Client, ClientNotFound
from MakerWeek.objects.event import Event
from MakerWeek.realtime.realtime import broadcastEvent
from flask import request, Blueprint
import json

api = Blueprint('api', __name__, url_prefix="/api")


@api.route("/get/client/<clientID>")
def getClientInfo(clientID):
    try:
        client=Client.getID(clientID)
    except ClientNotFound:
        return json.dumps({"msg": "no such client"}), 404
    client.getRecent()
    return json.dumps(client.toDict())


@api.route("/add/client")
def addClient():
    # API: Add new client
    # Parameters:
    #  - id: Uniquely identified ID
    #  - latitude, longitude: client's location in latitude and longitude
    #  TODO: - address: client's location in real world address
    # Returns
    #   TODO: Returns API key?

    __paramsList__ = {
        "clientID": "str",
        "latitude": "float",
        "longitude": "float",
        "address": "str"
    }
    params = paramsParse(__paramsList__, request.args)
    db = getDB()
    client = Client(**params)
    client.dbWrite()
    return json.dumps({"result": "success"})


@api.route("/add/event", methods=["POST", "GET"])
def addEntry():
    # API: Add events from a client
    # Parameters:
    #  - clientID: client id
    #  - temperature, humidity, dustLevel, coLevel: self-explanatory
    #  TODO: - apiKey: API key specific to that client
    # Returns:
    #  {"result": <result>}

    __paramsList__ = {
        "clientID": "str",
        "temperature": "float",
        "humidity": "float",
        "dustLevel": "float",
        "coLevel": "float"
    }
    params = paramsParse(__paramsList__, request.args)

    event = Event(**params)
    event.dbWrite()
    client = Client.getID(params["clientID"])
    client.lastEvent = event.eventID
    client.dbUpdate()
    broadcastEvent(**event.toDict(), **client.toDict())
    return json.dumps({"result": "success"})


@api.route("/burn")
def burn():
    Client.createTable()
    Event.createTable()
    return "ok"
