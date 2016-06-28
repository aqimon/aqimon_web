import datetime


class Event:
    @staticmethod
    def __getCurrentTimestamp():
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = int(now.timestamp() * 1000)
        return timestamp

    def __init__(self, clientID, temperature, humidity, dustLevel, coLevel, time=None, eventID=None):
        self.clientID = clientID
        self.temperature = temperature
        self.humidity = humidity
        self.dustLevel = dustLevel
        self.coLevel = coLevel
        if time is None:
            self.time = self.__getCurrentTimestamp()
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
