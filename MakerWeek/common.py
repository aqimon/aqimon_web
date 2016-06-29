import datetime
import random
import string

import bcrypt


def paramsParse(paramsList, paramsValue):
    params = {}
    for paramName, paramType in paramsList.items():
        tmp = paramsValue[paramName]
        if paramType == "int":
            tmp = int(tmp)
        elif paramType == "float":
            tmp = float(tmp)
        params[paramName] = tmp
    return params


def overThreshold(coLevel, dustLevel):
    return coLevel >= 0 and dustLevel >= 0


def timeSubtract(days=0, hours=0, minutes=0, seconds=0):
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return datetime.datetime.now(datetime.timezone.utc) - delta


def hashPassword(pwd):
    if type(pwd) is str:
        pwd = pwd.encode("utf-8")
    return bcrypt.hashpw(pwd, bcrypt.gensalt())


def checkPassword(hash, pwd):
    if type(pwd) is str:
        pwd = pwd.encode("utf-8")
    if type(hash) is str:
        hash = hash.encode("utf-8")
    return bcrypt.hashpw(pwd, hash) == hash


def genRandomString(length):
    rand = random.SystemRandom()
    letters = string.ascii_letters + string.digits
    return ''.join(rand.choice(letters) for _ in range(length))
