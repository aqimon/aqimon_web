import random
import time

import requests

random.seed()

while True:
    data = {
        "clientID": "tuankiet65",
        "temperature": random.randint(20, 30),
        "humidity": random.randint(60, 100),
        "dustLevel": random.randint(0, 10) / 10,
        "coLevel": random.randint(0, 10) / 10
    }
    req = requests.get("http://localhost:5000/api/add/event", params=data)
    print(req.text)
    time.sleep(2)
