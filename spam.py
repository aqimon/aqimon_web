import datetime
import random
import uuid

import requests

CLIENT_NUM = 100

def generateClientInfo(uuid):
    return {
        "name": uuid,
        "latitude": random.randint(-300, 300) / 10,
        "longitude": random.randint(-300, 300) / 10,
        "address": "{} Ngo Quyen".format(random.randint(0, 1696)),
        "private": "true",
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
    session.post("http://localhost:5000/login", data=data)


random.seed()
clients = []
counter = 0

session = requests.Session()
login(session)

print("Creating some random client...")
for i in range(CLIENT_NUM):
    clientUUID = uuid.uuid4()
    client = generateClientInfo(clientUUID)
    data = session.get("http://localhost:5000/ajax/add/client", params=client).json()
    print(data)
    clients.append((data['clientID'], data['apiKey']))

currTime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
delta = datetime.timedelta(minutes=5)

print("Now we do some spam")
while True:
    for uuid in clients:
        event = generateEvent(uuid)
        print(session.get("http://localhost:5000/add/event", params=event).text)
    currTime += delta
