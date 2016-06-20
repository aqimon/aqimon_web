import json
import time

from mail import Mail
from notification import Notification

from redis import StrictRedis

table = {
    "mail": Mail(),
    "notification": Notification()
}


def handler(msg):
    channel = msg['channel'].decode("utf-8")
    data = msg['data'].decode("utf-8")
    data = json.loads(data)
    print("Received msg in channel {}: {}".format(channel, data))
    table[channel].handler(data)


db = StrictRedis()
pubsub = db.pubsub(ignore_subscribe_messages=True)

print("Subscribing to channels...")
for channel in table.keys():
    pubsub.subscribe(channel)

print("Listening...")
while True:
    msg = pubsub.get_message()
    if msg is not None:
        handler(msg)
    time.sleep(0.001)
