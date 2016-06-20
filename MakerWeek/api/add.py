import json

from MakerWeek.async.async import sendNotification
from MakerWeek.common import paramsParse, overThreshold
from MakerWeek.objects.client import Client
from MakerWeek.objects.event import Event
from MakerWeek.realtime.realtime import broadcastEvent
from flask import request, g


def addClient():
    # API: Add new client
    # Parameters:
    #  - id: Uniquely identified ID
    #  - latitude, longitude: client's location in latitude and longitude
    #  - address: client's location in real world address
    # Returns
    #   TODO: Returns API key?

    __paramsList__ = {
        "clientID": "str",
        "latitude": "float",
        "longitude": "float",
        "address": "str",
    }
    if g.user is None:
        return "{result: 'need to login first'}"
    params = paramsParse(__paramsList__, request.args)
    params['owner'] = g.user.id
    client = Client(**params)
    client.dbWrite()
    return json.dumps({"result": "success"})


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
    if overThreshold(params['coLevel'], params['dustLevel']):
        sendNotification(params['clientID'])
    return json.dumps({"result": "success"})
