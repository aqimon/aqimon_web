import base64
import os

import bcrypt

from MakerWeek.database import getDB


def createTable():
    __tabledefinition__ = """
            CREATE TABLE loginToken (
                tokenKey VARCHAR NOT NULL PRIMARY KEY,
                tokenHash VARCHAR NOT NULL,
                userID INTEGER REFERENCES user(id)
            )
        """
    with getDB() as cursor:
        cursor.execute("DROP TABLE IF EXISTS loginToken")
        cursor.execute(__tabledefinition__)


def __init__(self):
    pass


def get(tokenKey, tokenValue):
    with getDB() as cursor:
        cursor.execute("SELECT * FROM loginToken WHERE tokenKey=?", (tokenKey,))
        result = cursor.fetchone()
        if result is None:
            raise LoginTokenNotFound
        tokenHash = result['tokenHash']
        if bcrypt.hashpw(password=tokenValue, salt=tokenHash) == tokenHash:
            return result['userID']
        else:
            raise LoginTokenNotCorrect


def create(userID):
    tokenKey = _genRandomString(32).decode("utf-8")
    tokenValue = _genRandomString(128)
    tokenHash = bcrypt.hashpw(password=tokenValue, salt=bcrypt.gensalt())
    with getDB() as cursor:
        cursor.execute("INSERT INTO loginToken VALUES (?, ?, ?)",
                       (tokenKey, tokenHash, userID))
    return (tokenKey, tokenValue)

def _genRandomString(byteNum):
    rand = os.urandom(byteNum)
    randString = base64.b64encode(rand)
    return randString

class LoginTokenNotFound(Exception):
    pass


class LoginTokenNotCorrect(Exception):
    pass
