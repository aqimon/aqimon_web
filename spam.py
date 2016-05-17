import random
import requests

random.seed()

while True:
	data={
		"id": 1001,
		"temp": random.randint(20, 30),
		"humid": random.randint(80, 100),
		"dust": random.randint(0, 10)/10,
		"co": random.randint(0, 10)/10
	}
	req=requests.get("https://makerw33d-tuankiet65.rhcloud.com/api/add/entry", params=data)
	print(req.text)
