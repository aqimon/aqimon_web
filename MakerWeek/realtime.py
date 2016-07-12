import flask_socketio as socketio
from flask import request
from peewee import fn, SQL

from MakerWeek.common import fromTimestamp, timeSubtract
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


def getEventRange(clientID, rangeFrom, rangeTo):
    # asumming 5 min interval
    database.connect()
    client = Client.get(Client.id == clientID)
    dateFrom = fromTimestamp(rangeFrom)
    dateTo = fromTimestamp(rangeTo)
    delta = dateTo - dateFrom
    if (delta.days <= 1):
        # range <= 1 day, return all
        # 288 points
        print("1 day query")
        events = (Event
                  .select()
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .order_by(Event.timestamp))
    elif (delta.days <= 3):
        # range <= 3 days, 10 minutes period
        # 432 points
        print("3 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval (MINUTE(timestamp) mod 10) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), fn.HOUR(Event.timestamp), SQL("MINUTE(timestamp) div 10"))
                  .order_by(Event.timestamp))
    elif (delta.days <= 7):
        # range <= 1 week, 20 minutes period
        # 504 points
        print("7 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval (MINUTE(timestamp) mod 20) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), fn.HOUR(Event.timestamp), SQL("MINUTE(timestamp) div 20"))
                  .order_by(Event.timestamp))
    elif (delta.days <= 30):
        # range <= 1 month, 2 hour period, average
        # 372 points per type
        print("30 days query")
        events = (Event
                  .select(SQL(
            "(timestamp - interval MINUTE(timestamp) MINUTE - interval SECOND(timestamp) SECOND) AS timestamp"),
            fn.AVG(Event.temperature).alias("temperature"),
            fn.AVG(Event.humidity).alias("humidity"),
            fn.AVG(Event.dustlevel).alias("dustlevel"),
            fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp), SQL("HOUR(timestamp) div 2"))
                  .order_by(Event.timestamp))
    else:
        print(">1 month query")
        # range >=1 month, 1 day period, average
        # min 365/366 datapoints per type
        events = (Event
                  .select(fn.DATE(Event.timestamp).alias("timestamp"),
                          fn.AVG(Event.temperature).alias("temperature"),
                          fn.AVG(Event.humidity).alias("humidity"),
                          fn.AVG(Event.dustlevel).alias("dustlevel"),
                          fn.AVG(Event.colevel).alias("colevel"))
                  .where((Event.client_id == client) & (Event.timestamp >= dateFrom) & (Event.timestamp <= dateTo))
                  .group_by(fn.DATE(Event.timestamp))
                  .order_by(Event.timestamp))
    return [event.toFrontendObject(include_id=False) for event in events]

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
    elif action == "getEventRange":
        return getEventRange(data['clientID'], data['from'], data['to'])
    else:
        return {"msg": "no such action"}


def broadcastEvent(obj):
    realtimeServer.send(obj, json=True, room="index")
    clientRoom = "client_{}".format(obj['clientID'])
    realtimeServer.send(obj, json=True, room=clientRoom)
