from flask import Blueprint
from .add import *
from .debug import *
from .get import *
from .notification import *

api = Blueprint('api', __name__, url_prefix="/api")

api.add_url_rule("/add/client", view_func=add.addClient)
api.add_url_rule("/add/event", view_func=add.addEntry)

api.add_url_rule("/debug/burn", view_func=debug.burn)
api.add_url_rule("/debug/mail", view_func=debug.debugMail)

api.add_url_rule("/get/client/<clientID>", view_func=get.getClientInfo)

api.add_url_rule("/notification/subscribe", view_func=notification.subscribe)
api.add_url_rule("/notification/unsubscribe", view_func=notification.unsubscribe)
api.add_url_rule("/notification/status", view_func=notification.status)
