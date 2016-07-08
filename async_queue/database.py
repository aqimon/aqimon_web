import datetime
import json
import uuid

from peewee import *

# database = MySQLDatabase(host=app.config['DB_HOST'],
#                          user=app.config['DB_USER'],
#                          password=app.config['DB_PASSWORD'],
#                          database=app.config['DB_USERNAME'],
#                          fields={"JSONArray": "varchar"})

database = MySQLDatabase(host="localhost",
                         user="e3",
                         password="e3e3e3e3",
                         database="e3",
                         fields={"JSONArray": "varchar"})


def utcTime():
    return datetime.datetime.now(datetime.timezone.utc)


class JSONArrayField(Field):
    db_field = "longtext"

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class BaseModel(Model):
    class Meta:
        database = database


class IncorrectPassword(Exception):
    pass


class User(BaseModel):
    # auto id field
    username = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True)
    phone = CharField()


class Client(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(default="Untitled")
    address = TextField()
    latitude = FloatField()
    longitude = FloatField()
    owner = ForeignKeyField(rel_model=User, to_field='id')
    subscriber_list = JSONArrayField(null=False, default=[])
    api_key = CharField(unique=True)


class Event(BaseModel):
    # auto id field
    client_id = ForeignKeyField(rel_model=Client, to_field='id')
    colevel = FloatField()
    dustlevel = FloatField()
    humidity = FloatField()
    temperature = FloatField()
    timestamp = DateTimeField(default=utcTime)

    def toFrontendObject(self, include_geo=False, include_id=True):
        response = {
            "timestamp": self.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "dustLevel": self.dustlevel,
            "coLevel": self.colevel
        }
        if include_geo:
            response.update({
                'latitude': self.client_id.latitude,
                'longitude': self.client_id.longitude,
                'address': self.client_id.address
            })
        if include_id:
            response.update({
                "clientID": str(self.client_id.id)
            })
        return response


class LastEvent(BaseModel):
    client_id = ForeignKeyField(rel_model=Client, to_field='id', primary_key=True)
    event_id = ForeignKeyField(rel_model=Event, to_field='id')
