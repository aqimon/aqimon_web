import random
import time
import uuid

import requests

CLIENT_NUM = 4


def generateClientInfo(uuid):
    return {
        "id": uuid,
        "latitude": random.randint(-300, 300) / 10,
        "longitude": random.randint(-300, 300) / 10,
        "address": "{} Ngo Quyen".format(random.randint(0, 1696))
    }


def generateEvent(uuid):
    return {
        "client_id": uuid[0],
        "temperature": random.randint(22, 35),
        "humidity": random.randint(0, 100),
        "dustlevel": random.randint(0, 10) / 10,
        "colevel": random.randint(0, 10) / 10,
        "apikey": uuid[1]
    }


def login(session):
    print("Logging in...")
    data = {
        "username": "spam_account",
        "password": "spam_account",
    }
    session.post("http://e3.tuankiet65.moe/login", data=data)


random.seed()
clients = []

session = requests.Session()
login(session)

print("Creating some random client...")
for i in range(CLIENT_NUM):
    clientUUID = uuid.uuid4()
    client = generateClientInfo(clientUUID)
    data = session.get("http://e3.tuankiet65.moe/ajax/add/client", params=client).json()
    print(data)
    clients.append((clientUUID, data['apiKey']))

print("Now we do some spam")
while True:
    for uuid in clients:
        event = generateEvent(uuid)
        session.get("http://e3.tuankiet65.moe/api/add/event", params=event)
        time.sleep(0.001)
