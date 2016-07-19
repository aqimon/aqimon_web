import json
import threading
import time

from redis import StrictRedis

from MakerWeek.async_queue.delete_client import DeleteClient
from MakerWeek.async_queue.export import ExportClient
from MakerWeek.async_queue.mail import Mail
from MakerWeek.async_queue.notification import Notification

table = {
    "mail": Mail(),
    "notification": Notification(),
    "delete_client": DeleteClient(),
    "export_client": ExportClient(),
    # "export_user": ExportUser()
}


def handler(msg):
    channel = msg['channel'].decode("utf-8")
    data = msg['data'].decode("utf-8")
    data = json.loads(data)
    print("Dispatching thread: {} {}".format(channel, data))
    thread = threading.Thread(target=table[channel].handler, args=(data,))
    thread.start()


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
