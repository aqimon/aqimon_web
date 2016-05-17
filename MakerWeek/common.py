import datetime

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