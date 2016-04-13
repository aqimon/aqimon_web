import json

import database
from flask import Flask, render_template, g, request

app = Flask(__name__)


def getDB():
    db = getattr(g, "db", None)
    if db is None:
        db = g.db = database.Database("maker_week.sqlite3")
    return db


@app.teardown_appcontext
def closeDB(e):
    db = getattr(g, "db", None)
    if db is not None:
        g.db.close()
    g.db = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/get/machine/<int:machineID>/<duration>")
def getMachineInfo(machineID, duration):
    db=getDB()
    q=db.getMachineData(machineID, duration)
    return json.dumps(q, indent=4)


@app.route("/api/get/recent")
def getRecentMachines():
    db = getDB()
    q = db.getRecentMachines()
    return json.dumps(q, indent=4)


@app.route("/api/add/entry")
def addEntry():
    # GET / POST
    # id=int temp=float humid=float dust=float co=float
    db = getDB()
    id=int(request.values['id'])
    temp=float(request.values['temp'])
    humid=float(request.values['humid'])
    dust=float(request.values['dust'])
    co=float(request.values['co'])
    db.addEntry(id, temp, humid, dust, co)
    return json.dumps({"result": "success"})

@app.route("/api/add/machine")
def addMachine():
    # GET / POST
    # id=int lat=float lon=float
    db = getDB()
    id=int(request.values['id'])
    lat=float(request.args['lat'])
    lon=float(request.args['lon'])
    db.addMachine(id, lat, lon)
    return json.dumps({"result": "success"})


if __name__ == "__main__":
    app.run(debug=True)
