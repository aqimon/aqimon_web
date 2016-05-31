from MakerWeek.database import getDB
from MakerWeek.authentication import loginToken
import bcrypt

class User:
    def __init__(self, userID):
        with getDB() as cursor:
            cursor.execute("SELECT * FROM user WHERE id=?", (userID, ))
            row=cursor.fetchone()
            if row is None:
                raise UserNotFound
            self.id=row['id']
            self.username=row['username']
            self.email=row['email']


def _createTable():
    with getDB() as cursor:
        cursor.execute("""CREATE TABLE user(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR NOT NULL UNIQUE,
                            password VARCHAR NOT NULL,
                            email VARCHAR NOT NULL UNIQUE
                        )""")

def _getHashesPassword(username):
    with getDB() as cursor:
        cursor.execute("SELECT id, password FROM user WHERE username=?", (username, ))
        row=cursor.fetchone()
        if row is None:
            raise UserNotFound
        return (row['id'], row['password'])

def login(username, password):
    try:
        userID, hash=_getHashesPassword(username)
    except UserNotFound:
        raise LoginFailed
    password=password.encode("utf-8")
    if bcrypt.hashpw(password, hash)!=hash:
        raise LoginFailed
    return loginToken.create(userID)

def createNewUser(username, password, email):
    password=password.encode("utf-8")
    password=bcrypt.hashpw(password, bcrypt.gensalt())
    with getDB() as cursor:
        cursor.execute("INSERT INTO user(username, password, email) VALUES (?, ?, ?)", (username, password, email))

class LoginFailed(Exception):
    pass

class UserNotFound(Exception):
    pass