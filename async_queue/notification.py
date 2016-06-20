import json
import sqlite3

from redis import StrictRedis


class Database:
    def __init__(self, fileName):
        self.db = sqlite3.connect(fileName)
        self.db.row_factory = sqlite3.Row

    def __enter__(self):
        cursor = self.db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.commit()

    def close(self):
        self.db.close()


class Notification:
    redis = StrictRedis()
    db = Database("../MakerWeek.sqlite3")

    def __init__(self):
        pass

    def handler(self, data):
        clientID = data['clientID']
        with self.db as cursor:
            cursor.execute("SELECT subscriberList FROM client WHERE clientID=?", (clientID,))
            result = cursor.fetchone()
        if result is None:
            return
        list = json.loads(result['subscriberList'])
        for userID in list:
            with self.db as cursor:
                cursor.execute("SELECT email FROM user WHERE id=?", (userID,))
                email = cursor.fetchone()['email']
            msg = json.dumps({
                "dst": email,
                "subject": "high {}".format(clientID),
                "msg": "high {}".format(clientID)
            })
            self.redis.publish("mail", msg)
