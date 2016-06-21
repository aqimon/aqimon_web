import json

from MakerWeek.objects.client import Client, ClientNotFound
from flask import request


def getClientInfo():
    clientID = request.args['clientID']
    try:
        client = Client.getID(clientID)
    except ClientNotFound:
        return json.dumps({"msg": "no such client"}), 404
    client.getRecent()
    return json.dumps(client.toDict())
