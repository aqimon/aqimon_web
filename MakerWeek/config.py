import os

from MakerWeek.common import genRandomString


class ProductionConfig(object):
    DEBUG = False
    PROPAGATE_EXCEPTIONS = False
    SERVER_NAME = "e3.tuankiet65.moe"
    ROOT_FOLDER = "/home/ubuntu/makerweek_web/MakerWeek/"


class DevelopmentConfig(object):
    DEBUG = True
    PROPAGATE_EXCEPTIONS = True
    SERVER_NAME = "localhost:5000"
    ROOT_FOLDER = "/home/tuankiet65/PycharmProjects/makerweek_web/MakerWeek/"


class Config(DevelopmentConfig):
    SECRET_KEY = genRandomString(256)
    PREFERRED_URL_SCHEME = "http"

    PORT = 5000

    DB_HOST = "localhost"
    DB_NAME = "e3"
    DB_USER = "root"
    DB_PASSWORD = "e3e3e3e3"

    AMAZON_ACCESS_KEY_ID = os.getenv("AMAZON_ACCESS_KEY_ID")
    AMAZON_SECRET_ACCESS_KEY = os.getenv("AMAZON_SECRET_ACCESS_KEY")

    def __init__(self):
        self.EXPORT_FOLDER = os.path.join(self.ROOT_FOLDER, "static/export")
        self.AVATAR_FOLDER = os.path.join(self.ROOT_FOLDER, "static/avatar")
