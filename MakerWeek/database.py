import sqlite3

class Database():
    def __init__(self, fileName):
        self.db = sqlite3.connect(fileName)
        self.db.row_factory = sqlite3.Row

    def __enter__(self):
        cursor=self.db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.commit()
        self.db.close()

    def close(self):
        self.db.close()

def getDB():
    return Database("MakerWeek.sqlite3")
