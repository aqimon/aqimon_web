import flask_socketio as socketio
from flask import request
from peewee import DoesNotExist

from MakerWeek.common import timeSubtract
from MakerWeek.database.database import database, Event, Client, LastEvent, WebsocketToken, InvalidToken

realtimeServer = socketio.SocketIO()


@realtimeServer.on("connect")
def sayWelcome():
    socketio.send({"msg": "Welcome to MakerWeek SocketIO server"},
                  json=True,
                  room=request.sid)


@realtimeServer.on("disconnect")
def sayGoodbye():
    socketio.send({"msg": "Goodbye and have a nice day"},
                  json=True,
                  room=request.sid)


def getRecent():
    database.connect()
    last_events = (LastEvent
                   .select(LastEvent, Event, Client)
                   .join(Event)
                   .join(Client)
                   .where((Event.timestamp >= timeSubtract(minutes=15)) & (~Client.private)))
    response = [last_event.event_id.toFrontendObject(include_geo=True) for last_event in last_events]
    database.close()
    return response


def getRecentPrivate(user):
    database.connect()
    last_events = (LastEvent
                   .select(LastEvent, Event, Client)
                   .join(Event)
                   .join(Client)
                   .where((Event.timestamp >= timeSubtract(minutes=15)) & (Client.owner == user)))
    response = [last_event.event_id.toFrontendObject(include_geo=True) for last_event in last_events]
    database.close()
    return response


def joinAllPrivateRooms(user):
    database.connect()
    clients = (Client
               .select()
               .where((Client.owner == user) & (Client.private)))
    for client in clients:
        socketio.join_room("client_{}".format(client.id))
    database.close()


def joinRoom(clientID, wsTokenKey=None, wsTokenValue=None):
    database.connect()
    if clientID == "index":
        socketio.join_room("index")
        return {"msg": "ok"}
    try:
        client = Client.get(Client.id == clientID)
    except DoesNotExist:
        return {"msg": "client not found"}
    if client.private:
        if (wsTokenKey is None) or (wsTokenValue is None):
            return {"msg": "need to auth"}
        try:
            _ = WebsocketToken.use(wsTokenKey, wsTokenValue)
        except InvalidToken:
            return {"msg": "invalid token"}
    socketio.join_room("client_{}".format(clientID))
    return {"msg": "ok"}


@realtimeServer.on("json")
def handleIncoming(data):
    action = data['action']
    if action == "joinClientRoom":
        if ('wsTokenKey' in data) and ('wsTokenValue' in data):
            return joinRoom(data['clientid'], data['wsTokenKey'], data['wsTokenValue'])
        else:
            return joinRoom(data['clientid'])
    elif action == "leaveClientRoom":
        if data['clientid'] == "index":
            socketio.leave_room("index")
        else:
            socketio.leave_room("client_{}".format(data['clientid']))
    elif action == "getRecent":
        res = getRecent()
        if ('wsTokenKey' in data) and ('wsTokenValue' in data):
            try:
                user = WebsocketToken.use(data['wsTokenKey'], data['wsTokenValue'])
            except InvalidToken:
                pass
            else:
                res += getRecentPrivate(user)
        return res
    elif action == "joinAllPrivateRooms":
        if ('wsTokenKey' not in data) or ('wsTokenValue' not in data):
            return {"msg": "need to auth"}
        else:
            try:
                user = WebsocketToken.use(data['wsTokenKey'], data['wsTokenValue'])
            except InvalidToken:
                return {"msg": "need to auth"}
        joinAllPrivateRooms(user)
        return {"msg": "ok"}
    else:
        return {"msg": "no such action"}


def broadcastEvent(obj, private=False):
    if not private:
        realtimeServer.send(obj, json=True, room="index")
    clientRoom = "client_{}".format(obj['id'])
    realtimeServer.send(obj, json=True, room=clientRoom)
