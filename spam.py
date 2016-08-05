import datetime
import random
import time

import requests

CLIENT_NUM = 2

def generateClientInfo(uuid):
    return {
        "name": uuid,
        "latitude": random.randint(-300, 300) / 10,
        "longitude": random.randint(-300, 300) / 10,
        "address": "{} Ngo Quyen".format(random.randint(0, 1696)),
        "private": "false",
        "tags": '["bot", "automatic", "testbot"]'
    }


def generateEvent(uuid):
    return {
        "client_id": uuid[0],
        "temperature": random.randint(22, 35),
        "humidity": random.randint(0, 100),
        "dustlevel": random.randint(0, 10) / 10,
        "colevel": random.randint(0, 10) / 10,
        "apikey": uuid[1],
        "time": int(currTime.timestamp()),
    }


def login(session):
    print("Logging in...")
    data = {
        "username": "x",
        "password": "x",
    }
    session.post("https://e3.tuankiet65.moe/login", data=data)


random.seed()
clients = []
counter = 0

session = requests.Session()
login(session)

# print("Creating some random client...")
# for i in range(CLIENT_NUM):
#     clientUUID = uuid.uuid4()
#     client = generateClientInfo(clientUUID)
#     data = session.get("http://localhost:5000/ajax/add/client", params=client).json()
#     print(data)
#     clients.append((data['clientID'], data['apiKey']))
#
currTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
# delta = datetime.timedelta(minutes=5)
# input()
xxxxx = ("e3aab777-1513-4f2f-8ed2-715951d2c308", "MagHF2DwdyEXrR2Kq91S")
print("Now we do some spam")
while True:
    event = generateEvent(xxxxx)
    print(session.get("https://e3.tuankiet65.moe/api/add/event", params=event).text)
    time.sleep(10)
