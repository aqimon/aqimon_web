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
            print("Client does not exist")
            return
        for userID in client.subscriber_list:
            user = User.get(User.id == userID)
            if data['status']:
                email = {
                    "dst": user.email,
                    "subject": "high {}".format(clientID),
                    "msg": "Client {} has high value readings, which indicates bad air quality.".format(clientID)
                }
            else:
                email = {
                    "dst": user.email,
                    "subject": "low {}".format(clientID),
                    "msg": "Client {} readings has gone normal.".format(clientID)
                }
            sendQueue("mail", json.dumps(email))
            email['dst'] = user.phone
            sendQueue("sms", json.dumps(email))
        database.close()
