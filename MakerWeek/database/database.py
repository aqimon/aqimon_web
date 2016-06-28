import base64
import datetime
import json
import os

from flask import session
from peewee import *

from MakerWeek.common import hashPassword, checkPassword

database = MySQLDatabase(host="localhost",
                         user="e3",
                         password="e3e3e3e3",
                         database="e3",
                         fields={"JSONArray": "varchar"})


def utcTime():
    return datetime.datetime.now(datetime.timezone.utc)


class JSONArrayField(Field):
    db_field = "varchar"

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

    def login(self, password):
        if not checkPassword(self.password, password):
            # TODO: exception
            raise Exception
        return LoginToken.create(self.id)

    @staticmethod
    def add(username, password, email):
        password = hashPassword(password)
        return User(username, password, email)

    @staticmethod
    def logout():
        session.clear()


class Client(BaseModel):
    id = UUIDField(primary_key=True)
    address = TextField()
    last_event = ForeignKeyField(rel_model=Event, to_field='id')
    latitude = FloatField()
    longitude = FloatField()
    owner = ForeignKeyField(rel_model=User, to_field='id')
    subscriber_list = JSONArrayField(null=False, default=[])


class Event(BaseModel):
    # auto id field
    client_id = ForeignKeyField(rel_model=Client, to_field='id')
    colevel = FloatField()
    dustlevel = FloatField()
    humidity = FloatField()
    temperature = FloatField()
    timestamp = DateTimeField(default=utcTime)

    def toFrontendObject(self):
        return {
            "timestamp": self.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp(),
            "temperature": self.temperature,
            "humidity": self.humidity,
            "dustLevel": self.dustlevel,
            "coLevel": self.colevel
        }


class ForgotToken(BaseModel):
    token = CharField(primary_key=True)
    timestamp = DateTimeField(default=utcTime)
    user_id = ForeignKeyField(rel_model=User, to_field='id')


class LoginToken(BaseModel):
    token_key = CharField(primary_key=True)
    token_hash = CharField()
    user_id = ForeignKeyField(rel_model=User, to_field='id')

    @staticmethod
    def create(user_id):
        token_key = LoginToken._genRandomString(32).decode("utf-8")
        token_value = LoginToken._genRandomString(128)
        token_hash = hashPassword(token_value)
        new = LoginToken(token_key, token_hash, user_id)
        return token_key, token_value

    @staticmethod
    def get(token_key, token_value):
        # TODO: Exception
        token_obj = LoginToken.get(LoginToken.token_key == token_key)
        if not checkPassword(token_obj.token_hash, token_value):
            # TODO: Exception
            raise Exception
        return token_obj.user_id

    @staticmethod
    def _genRandomString(byteNum):
        rand = os.urandom(byteNum)
        randString = base64.b64encode(rand)
        return randString
