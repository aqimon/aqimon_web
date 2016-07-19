import bz2
import csv
import gzip
import json

from MakerWeek.async_queue.redis import sendQueue
from MakerWeek.common import genRandomString, utcNow
from MakerWeek.database.database import database, Client, Event


class ExportClient:
    def __init__(self):
        pass

    def handler(self, data):
        database.connect()
        client = Client.get(Client.id == data['clientID'])
        formatTable = {
            "json": ".json",
            "csv": ".csv",
        }
        compressionTable = {
            "gzip": ".gz",
            "bzip2": ".bz2",
            "none": ""
        }

        try:
            fileExt = formatTable[data['format']]
        except ValueError:
            raise FileFormatNotSupported

        try:
            compExt = compressionTable[data['compression']]
        except ValueError:
            raise FileFormatNotSupported

        fileName = "../static/export/client/client_{username}_{clientid}_{time}_{random}{ext}{compExt}".format(
            username=client.owner.username,
            clientid=str(client.id),
            time=utcNow().timestamp(),
            random=genRandomString(6),
            ext=fileExt,
            compExt=compExt)

        if data['compression'] == "none":
            file = open(fileName, "w")
        elif data['compression'] == "gzip":
            file = gzip.open(fileName, "w")
        else:
            file = bz2.open(fileName, "w")

        events = (Event
                  .select(Event, Client)
                  .where(Event.client_id == client))
        events = [event.toFrontendObject(include_id=False) for event in events]

        if data['format'] == "json":
            self._writeJSONData(file, client, events)
        elif data['format'] == "csv":
            self._writeCSVData(file, events)
        file.close()
        sendQueue("mail", json.dumps({
            "dst": client.owner.email,
            "subject": "Export client {}".format(str(client.id)),
            "content": "client_{username}_{clientid}_{time}_{random}{ext}{compExt}"
        }))

    def _writeJSONData(self, file, client, events):
        data = client.toFrontendObject()
        data.update({
            "events": events
        })
        json.dump(data, file)

    def _writeCSVData(self, file, events):
        __fieldname__ = ["timestamp", "temperature", "humidity", "dustlevel", "colevel"]
        writer = csv.DictWriter(file, __fieldname__)
        writer.writeheader()
        writer.writerows(events)


class FileFormatNotSupported(Exception):
    pass
