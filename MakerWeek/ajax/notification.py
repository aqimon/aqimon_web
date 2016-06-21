import json

from MakerWeek.objects.client import Client
from flask import g, request


def subscribe():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.getID(clientID)
    client.subscribe(userID)
    client.dbUpdate()
    return json.dumps({"result": "success"})


def unsubscribe():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.getID(clientID)
    client.unsubscribe(userID)
    client.dbUpdate()
    return json.dumps({"result": "success"})


def status():
    clientID = request.args['clientID']
    if g.user is None:
        return json.dumps({"result": "Need to login"})
    userID = g.user.id
    client = Client.getID(clientID)
    if client.isSubscribed(userID):
        return json.dumps({"result": "yes"})
    else:
        return json.dumps({"result": "no"})
