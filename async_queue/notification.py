import json

from peewee import *
from redis import StrictRedis

database = MySQLDatabase(host="localhost",
                         user="e3",
                         password="e3e3e3e3",
                         database="e3",
                         fields={"JSONArray": "varchar"})


class JSONArrayField(Field):
    db_field = "longtext"

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    # auto id field
    username = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True)


class Client(BaseModel):
    id = UUIDField(primary_key=True)
    address = TextField()
    latitude = FloatField()
    longitude = FloatField()
    owner = ForeignKeyField(rel_model=User, to_field='id')
    subscriber_list = JSONArrayField(null=False, default=[])


class Notification:
    redis = StrictRedis()

    def __init__(self):
        pass

    def handler(self, data):
        clientID = data['clientID']
        try:
            client = Client.get(Client.id == clientID)
        except DoesNotExist:
            return
        for userID in client.subscriber_list:
            user = User.get(User.id == userID)
            msg = json.dumps({
                "dst": user.email,
                "subject": "high {}".format(clientID),
                "msg": "high {}".format(clientID)
            })
            self.redis.publish("mail", msg)
