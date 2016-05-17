import flask_socketio as socketio
from flask import request
from . import room, event

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


@realtimeServer.on("json")
def handleIncoming(data):
    # {"action": <str>, "room": <str>}
    # if action=join then room is the room to join
    # if action=leave then room is the room to leave
    # if action=recent then get recent client data
    action = data['action']
    if action == "joinRoom":
        room.joinRoom(data['room'])
    elif action == "leaveRoom":
        room.leaveRoom(data['room'])
    elif action == "getRecent":
        return event.getRecent()
    else:
        return {"msg": "no such action"}


def broadcastEvent(clientID, temperature, humidity, dustLevel, coLevel, time, longitude, latitude, address, **kwargs):
    data = {"clientID": clientID,
            "temperature": temperature,
            "humidity": humidity,
            "dustLevel": dustLevel,
            "coLevel": coLevel,
            "time": time,
            "longitude": longitude,
            "latitude": latitude,
            "address": address}
    realtimeServer.send(data, json=True, room="index")
    clientRoom = "client_{}".format(clientID)
    realtimeServer.send(data, json=True, room=clientRoom)
