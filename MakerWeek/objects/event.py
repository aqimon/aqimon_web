import datetime

class Event():
    @staticmethod
    def createTable(db):
        with db as cursor:
            __tabledefinition__ = """
                    CREATE TABLE event(
                        eventID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        clientID VARCHAR NOT NULL REFERENCES client(clientID),
                        time DATETIME NOT NULL,
                        temperature REAL NOT NULL,
                        humidity REAL NOT NULL,
                        dustLevel REAL NOT NULL,
                        coLevel REAL NOT NULL
                    )
                """
            cursor.execute("DROP TABLE IF EXISTS event")
            cursor.execute(__tabledefinition__)

    def __init__(self, clientID, temperature, humidity, dustLevel, coLevel, time=None, eventID=None):
        self.clientID = clientID
        self.temperature = temperature
        self.humidity = humidity
        self.dustLevel = dustLevel
        self.coLevel = coLevel
        if time is None:
            self.time = datetime.datetime.utcnow()
        else:
            if isinstance(time, str):
                self.time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.f")
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
            "time": self.time_to_sqlite()
        }

    def db_write(self, db):
        with db as cursor:
            cursor.execute(
                "INSERT INTO event (clientID, time, temperature, humidity, dustLevel, coLevel) VALUES (?, ?, ?, ?, ?, ?)",
                (self.clientID,
                 self.time_to_sqlite(),
                 self.temperature,
                 self.humidity,
                 self.dustLevel,
                 self.coLevel))
            self.eventID = cursor.lastrowid

    def time_to_sqlite(self):
        return self.time.isoformat(sep=" ")

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
