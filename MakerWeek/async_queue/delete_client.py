from MakerWeek.database.database import database, Client, LastEvent, Event


class DeleteClient():
    def __init__(self):
        pass

    def handler(self, data):
        clientID = data['clientID']
        database.connect()
        client = Client.get(Client.id == clientID)
        with database.atomic():
            LastEvent.delete().where(LastEvent.client_id == client).execute()
            Event.delete().where(Event.client_id == client).execute()
            client.delete_instance()
        database.close()
