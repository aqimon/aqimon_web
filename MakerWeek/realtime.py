import flask_socketio as socketio
from flask import request

from MakerWeek.common import timeSubtract
from MakerWeek.database.database import database, Event, Client, LastEvent

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
                   .where(Event.timestamp >= timeSubtract(minutes=15)))
    response = [last_event.event_id.toFrontendObject(include_geo=True) for last_event in last_events]
    database.close()
    return response

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
    clientRoom = "client_{}".format(obj['clientID'])
    realtimeServer.send(obj, json=True, room=clientRoom)
