import json

from peewee import *

from MakerWeek.async_queue.redis_helper import sendQueue
from MakerWeek.database.database import database, Client, User

class Notification:
    def __init__(self):
        pass

    def handler(self, data):
        database.connect()
        clientID = data['clientID']
        try:
            client = Client.get(Client.id == clientID)
        except DoesNotExist:
            return
        for userID in client.subscriber_list:
            user = User.get(User.id == userID)
            if data['status']:
                msg = json.dumps({
                    "dst": user.email,
                    "subject": "low {}".format(clientID),
                    "msg": "low {}".format(clientID)
                })
            else:
                msg = json.dumps({
                    "dst": user.email,
                    "subject": "low {}".format(clientID),
                    "msg": "low {}".format(clientID)
                })
            sendQueue("mail", msg)
        database.close()
