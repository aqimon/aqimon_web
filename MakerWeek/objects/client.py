from MakerWeek.database import getDB
import datetime

class Client():
    def __init__(self, clientID, longitude, latitude, address, lastEvent=None):
        self.clientID = clientID
        self.longitude = longitude
        self.latitude = latitude
        self.address = address
        self.lastEvent = lastEvent
        self.recentEvents=None

    def getRecent(self):
        timedelta = datetime.timedelta(days=1)
        time = datetime.datetime.now(datetime.timezone.utc) - timedelta
        timestamp = int(time.timestamp() * 1000)
        with getDB() as cursor:
            cursor.execute("""
                SELECT time, temperature, humidity, dustLevel, coLevel
                FROM event
                WHERE clientID=? AND time>?
                ORDER BY time ASC
            """, (self.clientID, timestamp))
            self.recentEvents=[]
            for row in cursor.fetchall():
                self.recentEvents.append(dict(row))


    def toDict(self):
        return {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "address": self.address,
            "recentEvents": self.recentEvents
        }

    def dbWrite(self):
        db=getDB()
        with db as cursor:
            cursor.execute("INSERT INTO client(clientID, longitude, latitude, address) VALUES (?, ?, ?, ?)",
                           (self.clientID,
                            self.latitude,
                            self.longitude,
                            self.address))

    def dbUpdate(self):
        db=getDB()
        with db as cursor:
            cursor.execute("UPDATE client SET longitude=?, latitude=?, address=?, lastEvent=? WHERE clientID=?",
                           (self.longitude,
                            self.latitude,
                            self.address,
                            self.lastEvent,
                            self.clientID))

    @staticmethod
    def getID(clientID):
        db = getDB()
        with db as cursor:
            cursor.execute("SELECT * FROM client WHERE clientID=?", (clientID,))
            result = cursor.fetchone()
            if result is None:
                raise ClientNotFound()
            else:
                return Client(**dict(result))

    @staticmethod
    def createTable():
        __tabledefinition__ = """
            CREATE TABLE client (
                clientID VARCHAR PRIMARY KEY,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address VARCHAR NOT NULL,
                lastEvent INTEGER
            )
        """
        db = getDB()
        with db as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DROP TABLE IF EXISTS client")
            cursor.execute(__tabledefinition__)


class ClientNotFound(Exception):
    pass
