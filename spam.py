import random
import time
import requests
import uuid

CLIENT_NUM=4

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

random.seed()
clients=[]

print("Creating some random client...")
for i in range(CLIENT_NUM):
    clientUUID=uuid.uuid4()
    clients.append(clientUUID)
    client=generateClientInfo(clientUUID)
    requests.get("http://localhost:5000/api/add/client", params=client)

print("Now we do some spam")
while True:
    for uuid in clients:
        event=generateEvent(uuid)
        requests.get("http://localhost:5000/api/add/event", params=event)
        time.sleep(0.5)
