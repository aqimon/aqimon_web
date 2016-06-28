import flask_socketio as socketio
from flask import request

from MakerWeek.common import timeSubtract
from MakerWeek.database.database import Event

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
    events = Event.select().where(Event.timestamp >= timeSubtract(minutes=15))
    return [event.toFrontendObject() for event in events]


@realtimeServer.on("json")
def handleIncoming(data):
    # {"action": <str>, "room": <str>}
    # if action=join then room is the room to join
    # if action=leave then room is the room to leave
    # if action=recent then get recent client data
    action = data['action']
    if action == "joinRoom":
        socketio.join_room(data['room'])
    elif action == "leaveRoom":
        socketio.leave_room(data['room'])
    elif action == "getRecent":
        return getRecent()
    else:
        return {"msg": "no such action"}


def broadcastEvent(obj):
    realtimeServer.send(obj, json=True, room="index")
    clientRoom = "client_{}".format(clientID)
    realtimeServer.send(obj, json=True, room=clientRoom)
