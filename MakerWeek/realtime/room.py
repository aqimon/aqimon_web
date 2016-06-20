import flask_socketio as socketio


def joinRoom(room):
    socketio.join_room(room)


def leaveRoom(room):
    socketio.leave_room(room)
