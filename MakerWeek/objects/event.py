import datetime

from MakerWeek.database import getDB

class Event():

    @staticmethod
    def __getCurrentTimestamp__():
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = int(now.timestamp() * 1000)
        return timestamp

    @staticmethod
    def createTable():
        db=getDB()
        with db as cursor:
            __tabledefinition__ = """
                    CREATE TABLE event(
                        eventID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        clientID VARCHAR NOT NULL REFERENCES client(clientID),
                        time INTEGER NOT NULL,
                        temperature REAL NOT NULL,
                        humidity REAL NOT NULL,
                        dustLevel REAL NOT NULL,
                        coLevel REAL NOT NULL
                    )
                """
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DROP TABLE IF EXISTS event")
            cursor.execute(__tabledefinition__)

    def __init__(self, clientID, temperature, humidity, dustLevel, coLevel, time=None, eventID=None):
        self.clientID = clientID
        self.temperature = temperature
        self.humidity = humidity
        self.dustLevel = dustLevel
        self.coLevel = coLevel
        if time is None:
            self.time = self.__getCurrentTimestamp__()
        else:
            if isinstance(time, int):
                self.time = datetime.datetime.utcfromtimestamp(time)
            elif isinstance(time, datetime.datetime):
                self.tine = time
        if eventID is not None:
            self.eventID = eventID

    def toDict(self):
        return {
            "clientID": self.clientID,
            "eventID": self.eventID,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "dustLevel": self.dustLevel,
            "coLevel": self.coLevel,
            "time": self.time
        }

    def dbWrite(self):
        db = getDB()
        with db as cursor:
            cursor.execute(
                "INSERT INTO event (clientID, time, temperature, humidity, dustLevel, coLevel) VALUES (?, ?, ?, ?, ?, ?)",
                (self.clientID,
                 self.time,
                 self.temperature,
                 self.humidity,
                 self.dustLevel,
                 self.coLevel))
            self.eventID = cursor.lastrowid


    @staticmethod
    def get_event_via_id(db, eventID):
        with db as cursor:
            cursor.execute("SELECT * FROM event WHERE eventID=?", (eventID,))
            result = cursor.fetchone()
            if result is None:
                raise EventNotFound(id=eventID)
            else:
                return Event(**dict(result))


class EventNotFound(Exception):
    pass
