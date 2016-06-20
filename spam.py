import random
import time
import uuid

import requests

CLIENT_NUM = 4


def generateClientInfo(uuid):
    return {
        "clientID": uuid,
        "latitude": random.randint(-300, 300) / 10,
        "longitude": random.randint(-300, 300) / 10,
        "address": "{} Ngo Quyen".format(random.randint(0, 1696))
    }


def generateEvent(uuid):
    return {
        "clientID": uuid,
        "temperature": random.randint(22, 35),
        "humidity": random.randint(0, 100),
        "dustLevel": random.randint(0, 10) / 10,
        "coLevel": random.randint(0, 10) / 10
    }


def login(session):
    print("Logging in...")
    data = {
        "username": "test_account",
        "password": "test_account",
    }
    req = session.post("http://localhost:5000/login", data=data)


random.seed()
clients = []

session = requests.Session()
login(session)

print("Creating some random client...")
for i in range(CLIENT_NUM):
    clientUUID = uuid.uuid4()
    clients.append(clientUUID)
    client = generateClientInfo(clientUUID)
    print(session.get("http://localhost:5000/api/add/client", params=client).text)

print("Now we do some spam")
while True:
    for uuid in clients:
        event = generateEvent(uuid)
        session.get("http://localhost:5000/api/add/event", params=event)
        time.sleep(1)
