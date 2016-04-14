import sqlite3


class Database:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.conn = self.db.cursor()

    def initDB(self):
        self.conn.execute("DROP TABLE IF EXISTS machine")
        self.conn.execute("DROP TABLE if EXISTS entry")
        self.conn.execute(
            """CREATE TABLE machine(
                id INT NOT NULL PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                lastEntry INT)""")
        self.conn.execute(
            """CREATE TABLE entry(
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    machineID INTEGER NOT NULL,
                    time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL,
                    humidity REAL,
                    dustLevel REAL,
                    coLevel REAL)""")
        self.db.commit()

    def close(self):
        self.db.commit()
        self.db.close()

    def addMachine(self, id, lat, lon):
        self.conn.execute("INSERT INTO machine VALUES(?, ?, ?, NULL)", (id, lat, lon))
        self.db.commit()

    def addEntry(self, machineID, temp, humi, dust, co):
        query = self.conn.execute(
            "INSERT INTO entry(machineID, temperature, humidity, dustLevel, coLevel) VALUES (?, ?, ?, ?, ?)",
            (machineID, temp, humi, dust, co))
        entryID = query.lastrowid
        self.conn.execute("UPDATE machine SET lastEntry=? WHERE id=?", (entryID, machineID))
        self.db.commit()

    def getRecentMachines(self):
        fields = ("machineID", "latitude", "longitude", "temperature", "humidity", "dustLevel", "coLevel", "time")
        q = self.conn.execute(
            """SELECT machineID, latitude, longitude, temperature, humidity, dustLevel, coLevel, time
                FROM machine OUTER LEFT JOIN entry ON machine.lastEntry=entry.id
                WHERE time>datetime('now', '-1555 minutes')""")
        result = []
        for res in q:
            result.append(dict(zip(fields, res)))
        return result

    def getMachineData(self, machineID, timeOffset):
        fields = ("time", "temperature", "humidity", "dustLevel", "coLevel")
        q1 = list(self.conn.execute("SELECT * FROM machine WHERE id=?", (machineID, )))[0]
        q2 = self.conn.execute("""SELECT time, temperature, humidity, dustLevel, coLevel
                                FROM entry
                                WHERE machineID=? AND time>datetime('now', ?)""", (machineID, timeOffset))
        q2 = list(q2)
        res1 = {"id": q1[0], "lat": q1[1], "lon": q1[2]}
        res2 = []
        for tmp in q2:
            res2.append(dict(zip(fields, tmp)))
        res1['data'] = res2
        return res1
