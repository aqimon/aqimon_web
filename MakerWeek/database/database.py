import datetime
import json
import uuid

from flask import session
from peewee import *

from MakerWeek.common import hashPassword, checkPassword, genRandomString, genRandomNumber
from MakerWeek.config import Config

database = MySQLDatabase(host=Config.DB_HOST,
                         user=Config.DB_USER,
                         password=Config.DB_PASSWORD,
                         database=Config.DB_NAME,
                         fields={"JSONArray": "varchar"})


def utcTime():
    return datetime.datetime.now(datetime.timezone.utc)


def createAllTables():
    # first: create all tables
    database.create_tables(
        [User, Client, Event, ForgotToken, LoginToken, LastEvent, Tags, TagsMap, WebsocketToken, PhoneVerification],
        safe=False)
    # second: create fulltext index:
    database.execute_sql("ALTER TABLE client ADD FULLTEXT(name)")
    database.execute_sql("ALTER TABLE client ADD FULLTEXT(description)")
    database.execute_sql("ALTER TABLE tags ADD FULLTEXT(title)")
    database.execute_sql("ALTER TABLE tags ADD FULLTEXT(description)")
    database.execute_sql("ALTER TABLE user ADD FULLTEXT(username)")
    database.execute_sql("ALTER TABLE user ADD FULLTEXT(realname)")
    return json.dumps({"result": "success"})


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
    username = CharField(unique=True, max_length=100)
    password = CharField()
    email = CharField(unique=True, max_length=100)
    phone = CharField(default="")
    avatar = CharField(default="noavatar.png")
    realname = CharField(default="")

    def login(self, password):
        if not checkPassword(self.password, password):
            raise IncorrectPassword
        return LoginToken.new(self.id)

    @staticmethod
    def add(username, password, email, realname):
        password = hashPassword(password)
        User.create(username=username, password=password, email=email, realname=realname)

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
    description = TextField(default="")
    subscriber_list = JSONArrayField(null=False, default=[])
    api_key = CharField(default=lambda: genRandomString(20), unique=True, max_length=20)
    last_notification = BooleanField(default=False)
    private = BooleanField(default=False)

    temperature_limit = FloatField(default = 10)
    humidity_limit = FloatField(default = 10)
    colevel_limit = FloatField(default = 10)
    dustlevel_limit = FloatField(default = 10)

    def toFrontendObject(self):
        response = {
            'id': str(self.id),
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.id,
            'owner_username': self.owner.username,
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

    def toFrontendObject(self, include_geo=False, include_id=True, include_owner=False):
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
                "id": str(self.client_id.id),
                "name": self.client_id.name,
                'tags': [tag.title for tag in self.client_id.getTags()],
            })
        if include_owner:
            response.update({
                "owner_username": self.client_id.owner.username,
                "owner_realname": self.client_id.owner.realname
            })
        return response


class LastEvent(BaseModel):
    client_id = ForeignKeyField(rel_model=Client, to_field='id', primary_key=True)
    event_id = ForeignKeyField(rel_model=Event, to_field='id')


class ForgotToken(BaseModel):
    token = CharField(primary_key=True, default=lambda: genRandomString(128), max_length=128)
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
    token_key = CharField(primary_key=True, max_length=32)
    token_hash = CharField(max_length=128)
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
    title = CharField(index=True, unique=True, max_length=100)
    description = TextField(default="")


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
    token_key = CharField(primary_key=True, max_length=32)
    token_hash = CharField(max_length=128)

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


class PhoneVerification(BaseModel):
    phone = CharField(max_length=50)
    user_id = ForeignKeyField(rel_model=User, to_field="id", index=True, unique=True)
    verifyCode = IntegerField(default=lambda: genRandomNumber(100000, 999999))
    timestamp = DateTimeField(default=utcTime)
    tryCount = IntegerField(default=0)
