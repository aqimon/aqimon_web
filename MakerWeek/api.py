import json

from MakerWeek.common import paramsParse
from MakerWeek.database import getDB
from MakerWeek.objects.client import Client, ClientNotFound
from MakerWeek.objects.event import Event
from MakerWeek.realtime.realtime import broadcastEvent
from MakerWeek.mail import mail
from flask import request, Blueprint
import json
import random

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
    #  - address: client's location in real world address
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

@api.route("/debug/mail")
def debugMail():
    random.seed()
    tsundereQuote=random.choice([
        "N-No, it's not like I did it for you! I did it because I had freetime, that's all! ┐(￣ヘ￣;)┌",
        "I like you, you idiot!", # Jackpot m8
        "BAKAAAAAAAAAAAAAAA!!!!! YOU'RE A BAKAAAAAAA!!!!",
        "I'm just here because I had nothing else to do!",
        "Are you stupid?",
        "You're such a slob!",
        "You should be grateful!",
        "You're free anyways, right?",
        "Don't misunderstand, it's not like I like you or anything...",
        "H-Hey....( //・.・ // )",
        "....T-Thanks.....",
        "T-Tch! S-Shut up!",
        "I just had extra, so shut up and take it!",
        "Can you be ANY MORE CLUELESS?",
        "HEY! It's a privilege to even be able to talk to me! You should be honored!",
        "Geez, stop pushing yourself! You're going to get yourself hurt one day, you idiot!"
    ])
    mail.sendEmail("tuankiet65@gmail.com", "Tsundere quote", tsundereQuote)
    return "xxx"