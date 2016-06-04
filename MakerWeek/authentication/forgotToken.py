import base64
import datetime
import os

from MakerWeek.database import getDB


def createTable():
    __tabledefinition__ = """
        CREATE TABLE forgotToken(
            token VARCHAR NOT NULL PRIMARY KEY,
            userID INTEGER NOT NULL REFERENCES user(id),
            timestamp INTEGER NOT NULL
        )
    """

    with getDB() as cursor:
        cursor.execute("DROP TABLE IF EXISTS forgotToken")
        cursor.execute(__tabledefinition__)


def _genRandomString(byteNum):
    rand = os.urandom(byteNum)
    randString = base64.urlsafe_b64encode(rand)
    return randString


def generateForgotToken(userID):
    forgotToken = _genRandomString(30).decode("utf-8")
    time = datetime.datetime.now(datetime.timezone.utc)
    timestamp = time.timestamp() * 1000
    with getDB() as cursor:
        cursor.execute("INSERT INTO forgotToken VALUES (?, ?, ?)", (forgotToken, userID, timestamp))
    return (forgotToken, time + datetime.timedelta(days=1))


def useForgotToken(forgotToken):
    with getDB() as cursor:
        cursor.execute("SELECT * FROM forgotToken WHERE token=?", (forgotToken,))
        result = cursor.fetchone()
    if result is None:
        raise TokenNotFound
    currTime = datetime.datetime.now(datetime.timezone.utc)
    time = datetime.datetime.fromtimestamp(result['timestamp'] / 1000, datetime.timezone.utc) + datetime.timedelta(
        days=1)
    if currTime > time:
        raise TokenExpired
    with getDB() as cursor:
        cursor.execute("DELETE FROM forgotToken WHERE token=?", (forgotToken,))
    return result['userID']


class TokenNotFound(Exception):
    pass


class TokenExpired(Exception):
    pass
