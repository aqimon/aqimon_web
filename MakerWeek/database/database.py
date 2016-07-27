import datetime
import json
import uuid

from flask import session
from peewee import *

from MakerWeek.common import hashPassword, checkPassword, genRandomString
from MakerWeek.config import Config

database = MySQLDatabase(host=Config.DB_HOST,
                         user=Config.DB_USER,
                         password=Config.DB_PASSWORD,
                         database=Config.DB_NAME,
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

    def login(self, password):
        if not checkPassword(self.password, password):
            raise IncorrectPassword
        return LoginToken.new(self.id)

    @staticmethod
    def add(username, password, email, phone):
        password = hashPassword(password)
        User.create(username=username, password=password, email=email, phone=phone)

    @staticmethod
    def logout():
        session.clear()


class Client(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(default="Untitled")
    address = TextField()
    latitude = FloatField()
    longitude = FloatField()
    owner = ForeignKeyField(rel_model=User, to_field='id')
    subscriber_list = JSONArrayField(null=False, default=[])
    api_key = CharField(default=lambda: genRandomString(20), unique=True)
    last_notification = BooleanField(default=False)
    private = BooleanField(default=False)

    def toFrontendObject(self):
        response = {
            'id': str(self.id),
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.id,
            'tags': [tag.title for tag in self.getTags()],
            'private': self.private
        }
        return response

    def getTags(self):
        tags = [tagsMap.tag_id for tagsMap in TagsMap.select().join(Tags).where(TagsMap.client_id == self.id)]
        return tags


class Event(BaseModel):
    # auto id field
    client_id = ForeignKeyField(rel_model=Client, to_field='id')
    colevel = FloatField()
    dustlevel = FloatField()
    humidity = FloatField()
    temperature = FloatField()
    timestamp = DateTimeField()

    def toFrontendObject(self, include_geo=False, include_id=True):
        if type(self.timestamp) is datetime.date:
            self.timestamp = datetime.datetime(self.timestamp.year,
                                               self.timestamp.month,
                                               self.timestamp.day)
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
                "clientID": str(self.client_id.id),
                "name": self.client_id.name
            })
        return response


class LastEvent(BaseModel):
    client_id = ForeignKeyField(rel_model=Client, to_field='id', primary_key=True)
    event_id = ForeignKeyField(rel_model=Event, to_field='id')


class ForgotToken(BaseModel):
    token = CharField(primary_key=True, default=lambda: genRandomString(128))
    timestamp = DateTimeField(default=utcTime)
    user_id = ForeignKeyField(rel_model=User, to_field='id')

    @staticmethod
    def new(user_id):
        ForgotToken.delete().where(ForgotToken.user_id == user_id).execute()
        token = ForgotToken.create(user_id=user_id)
        return token


class InvalidToken(Exception):
    pass


class LoginToken(BaseModel):
    token_key = CharField(primary_key=True)
    token_hash = CharField()
    user_id = ForeignKeyField(rel_model=User, to_field='id')

    @staticmethod
    def new(user_id):
        token_key = genRandomString(32)
        token_value = genRandomString(128)
        token_hash = hashPassword(token_value)
        LoginToken.create(token_key=token_key, token_hash=token_hash, user_id=user_id)
        return token_key, token_value

    @staticmethod
    def use(token_key, token_value):
        try:
            token_obj = LoginToken.get(LoginToken.token_key == token_key)
        except DoesNotExist:
            raise InvalidToken
        if not checkPassword(token_obj.token_hash, token_value):
            raise InvalidToken
        return token_obj.user_id


class Tags(BaseModel):
    title = CharField(index=True)


class TagsMap(BaseModel):
    tag_id = ForeignKeyField(rel_model=Tags, to_field="id", index=True)
    client_id = ForeignKeyField(rel_model=Client, to_field="id", index=True)

    @staticmethod
    def link(client, tags):
        with database.atomic():
            TagsMap.delete().where(TagsMap.client_id == client).execute()
            for tagTitle in tags:
                tag, _ = Tags.get_or_create(title=tagTitle)
                TagsMap.create(tag_id=tag, client_id=client)


class WebsocketToken(BaseModel):
    user_id = ForeignKeyField(rel_model=User, to_field="id")
    token_key = CharField(primary_key=True)
    token_hash = CharField()

    @staticmethod
    def new(user_id):
        token_key = genRandomString(32)
        token_value = genRandomString(128)
        token_hash = hashPassword(token_value)
        WebsocketToken.create(token_key=token_key, token_hash=token_hash, user_id=user_id)
        return token_key, token_value

    @staticmethod
    def use(token_key, token_value):
        try:
            token_obj = WebsocketToken.get(WebsocketToken.token_key == token_key)
        except DoesNotExist:
            raise InvalidToken
        if not checkPassword(token_obj.token_hash, token_value):
            raise InvalidToken
        return token_obj.user_id
