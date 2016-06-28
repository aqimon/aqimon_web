import datetime

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


def timeSubtract(years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    delta = datetime.timedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
    return datetime.datetime.now() - delta


def hashPassword(pwd):
    return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())


def checkPassword(hash, pwd):
    return bcrypt.hashpw(pwd.encode("utf-8"), hash) == pwd
