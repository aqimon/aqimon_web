import datetime
import random

from MakerWeek.common import genRandomString
from MakerWeek.database.database import database, Event

database.connect()


def generateEvent(uuid):
    return {
        "client_id": "843ccd7f-93bb-496c-bb8b-f237fe905655",
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
    return [genRandomString(4) for _ in range(6)]


currTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
delta = datetime.timedelta(minutes=5)
clients = []

# print("client spam")
# with database.atomic():
#     for _ in range(1000):
#         clients.append(Client.create(**generateClient()))
#         TagsMap.link(clients[-1], generateRandomTags())
#         event = Event.create(**generateEvent(clients[-1]))
#         LastEvent.create(client_id=clients[-1], event_id=event)
#         if _ % 100 == 0:
#             print(_)

events = []
#
# c = Client.create(**generateClient())
# print("Created new client has UUID {}".format(str(c.id)))

print("Now we do some spam")
for i in range(10000):
    events.append(generateEvent("xxx"))
    currTime -= delta

print("Generated {} entries".format(len(events)))

with database.atomic():
    for i in range(0, len(events), 1000):
        print("Import from {} to {}".format(i, i + 1000), end="\r")
        Event.insert_many(events[i:i + 1000]).execute()
