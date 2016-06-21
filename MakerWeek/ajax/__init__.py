from flask import Blueprint
from .get import *
from .notification import *
from .user_settings import *

ajax = Blueprint('ajax', __name__, url_prefix="/ajax")

ajax.add_url_rule("/user_settings/save_general", view_func=saveGeneralSettings)
ajax.add_url_rule("/user_settings/change_password", view_func=changePassword)

ajax.add_url_rule("/get/client", view_func=get.getClientInfo)

ajax.add_url_rule("/notification/subscribe", view_func=notification.subscribe)
ajax.add_url_rule("/notification/unsubscribe", view_func=notification.unsubscribe)
ajax.add_url_rule("/notification/status", view_func=notification.status)
