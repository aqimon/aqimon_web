from MakerWeek.common import genRandomString


class ProductionConfig(object):
    DEBUG = False
    PROPAGATE_EXCEPTIONS = False
    SERVER_NAME = "e3.tuankiet65.moe"
    SECRET_KEY = genRandomString(256)
    DB_HOST = "localhost"
    DB_NAME = "e3"
    DB_USER = "e3"
    DB_PASSWORD = "e3e3e3e3"


class DevelopmentConfig(object):
    DEBUG = True
    PROPAGATE_EXCEPTIONS = True
    SECRET_KEY = genRandomString(256)

    DB_HOST = "localhost"
    DB_NAME = "e3"
    DB_USER = "e3"
    DB_PASSWORD = "e3e3e3e3"
