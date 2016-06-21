from flask import Blueprint
from .user_settings import *

ajax = Blueprint('ajax', __name__, url_prefix="/ajax")

ajax.add_url_rule("/user_settings/save_general", view_func=saveGeneralSettings)
ajax.add_url_rule("/user_settings/change_password", view_func=changePassword)
