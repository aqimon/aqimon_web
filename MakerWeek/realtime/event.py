from MakerWeek.database import getDB
import datetime

def getRecent():
    timedelta = datetime.timedelta(minutes=15)
    time = datetime.datetime.now(datetime.timezone.utc) - timedelta
    timestamp=int(time.timestamp()*1000)
    db=getDB()
    with db as cursor:
        cursor.execute("""SELECT client.clientID, latitude, longitude, time, temperature, humidity, dustLevel, coLevel, address
                       FROM client INNER JOIN event
                       ON lastEvent=eventID
                       WHERE time>?""", (timestamp,))
        events=[]
        for row in cursor.fetchall():
            events.append(dict(row))
        return events
