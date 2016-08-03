import bz2
import csv
import gzip
import json
import os

from MakerWeek.async_queue.redis_helper import sendQueue
from MakerWeek.common import utcNow
from MakerWeek.config import Config
from MakerWeek.database.database import database, Client, Event

config = Config()

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

        fileName = "client_{username}_{clientid}_{time}{ext}{compExt}".format(
            username=client.owner.username,
            clientid=str(client.id),
            time=int(utcNow().timestamp()),
            ext=fileExt,
            compExt=compExt)
        filePath = os.path.join(config.EXPORT_FOLDER, fileName)

        if data['compression'] == "none":
            file = open(filePath, "w")
        elif data['compression'] == "gzip":
            file = gzip.open(filePath, "wt")
        else:
            file = bz2.open(filePath, "wt")

        events = (Event
                  .select(Event, Client)
                  .join(Client)
                  .where(Event.client_id == client))
        events = [event.toFrontendObject(include_id=False) for event in events]

        if data['format'] == "json":
            self._writeJSONData(file, client, events)
        elif data['format'] == "csv":
            self._writeCSVData(file, events)
        file.close()
        link = "{http}://{domain}/static/export/{fileName}".format(http=Config.PREFERRED_URL_SCHEME,
                                                                   domain=Config.SERVER_NAME,
                                                                   fileName=fileName)
        sendQueue("mail", json.dumps({
            "dst": client.owner.email,
            "subject": "Export client {}".format(str(client.id)),
            "msg": "<a href=\"{link}\">{link}</a>".format(link=link)
        }))

    def _writeJSONData(self, file, client, events):
        data = client.toFrontendObject()
        data.update({
            "events": events
        })
        json.dump(data, file, indent=4)

    def _writeCSVData(self, file, events):
        __fieldname__ = ["timestamp", "temperature", "humidity", "dustLevel", "coLevel"]
        writer = csv.DictWriter(file, __fieldname__)
        writer.writeheader()
        writer.writerows(events)


class FileFormatNotSupported(Exception):
    pass
