from MakerWeek.database.database import database, Client


class DeleteClient():
    def __init__(self):
        pass

    def handler(self, data):
        clientID = data['clientID']
        database.connect()
        client = Client.get(Client.id == clientID)
