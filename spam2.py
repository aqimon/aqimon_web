import datetime
import random

from MakerWeek.common import genRandomString
from MakerWeek.database.database import database, Event, Client, TagsMap, LastEvent

database.connect()


def generateEvent(uuid):
    return {
        "client_id": uuid,
        "temperature": random.randint(22, 35),
        "humidity": random.randint(0, 100),
        "dustlevel": random.randint(0, 10) / 10,
        "colevel": random.randint(0, 10) / 10,
        "timestamp": currTime
    }


def generateClient():
    return {
        "name": " ".join([genRandomString(5) for _ in range(5)]),
        "latitude": 0.0,
        "longitude": 0.0,
        "address": "aaaa",
        "owner": 1
    }


def generateRandomTags():
    return [genRandomString(4) for _ in range(5)]


currTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
delta = datetime.timedelta(minutes=5)
clients = []

print("client spam")
with database.atomic():
    for _ in range(1000):
        clients.append(Client.create(**generateClient()))
        TagsMap.link(clients[-1], generateRandomTags())
        event = Event.create(**generateEvent(clients[-1]))
        LastEvent.create(client_id=clients[-1], event_id=event)
        if _ % 100 == 0:
            print(_)


# print("Now we do some spam")
# while currTime.year>=2013:
#     events.append(generateEvent())
#     currTime-=delta
#
# print("Generated {} entries".format(len(events)))
#
# with database.atomic():
#     for i in range(0, len(events), 1000):
#         print("Import from {} to {}".format(i, i+1000), end="\r")
#         Event.insert_many(events[i:i+1000]).execute()
