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
    redis.publish("deleteclient", json.dumps({"clientID": clientID}))
