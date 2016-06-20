import json

from MakerWeek.database import getRedis


def sendMail(dst, subject, content):
    redis = getRedis()
    msg = json.dumps({
        "dst": dst,
        "subject": subject,
        "msg": content
    })
    redis.publish("mail", msg)


def sendNotification(clientID):
    redis = getRedis()
    redis.publish("notification", json.dumps({"clientID": clientID}))
