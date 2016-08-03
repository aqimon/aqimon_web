import json

from flask import g
from redis import StrictRedis


def getRedis():
    if getattr(g, "redis", None) is None:
        g.redis = StrictRedis()
    return g.redis


def sendMail(dst, subject, content):
    redis = getRedis()
    msg = json.dumps({
        "dst": dst,
        "subject": subject,
        "msg": content
    })
    redis.publish("mail", msg)


def sendNotification(clientID, status):
    redis = getRedis()
    redis.publish("notification", json.dumps({"clientID": clientID, "status": status}))


def deleteClient(clientID):
    redis = getRedis()
    redis.publish("delete_client", json.dumps({"clientID": clientID}))


def exportClient(clientID, format, compression):
    redis = getRedis()
    redis.publish("export_client", json.dumps({"clientID": clientID, "format": format, "compression": compression}))
