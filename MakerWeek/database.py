import sqlite3

from flask import g
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


def getDB():
    if getattr(g, "db", None) is None:
        g.db = Database("MakerWeek.sqlite3")
    return g.db


def getRedis():
    if getattr(g, "redis", None) is None:
        g.redis = StrictRedis()
    return g.redis
