import json

import bcrypt
from MakerWeek.database import getDB
from flask import request, redirect, g, session


def saveGeneralSettings():
    if g.user is None:
        redirect("/login?needToLogin")
    newUsername = request.args['username']
    newEmail = request.args['email']
    with getDB() as cursor:
        cursor.execute("UPDATE user SET username=?, email=? WHERE id=?", (newUsername, newEmail, g.user.id))
    return json.dumps({"result": "success"})


def changePassword():
    if g.user is None:
        redirect("/login?needToLogin")
    oldPassword = request.args['old_password']
    with getDB() as cursor:
        cursor.execute("SELECT password FROM user WHERE id=?", (g.user.id,))
        hashedOldPassword = cursor.fetchone()['password']
    if bcrypt.hashpw(oldPassword.encode("utf-8"), hashedOldPassword) != hashedOldPassword:
        return json.dumps({"result": "incorrect old password"})
    newPassword = request.args['new_password']
    hashedNewPassword = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt())
    with getDB() as cursor:
        cursor.execute("UPDATE user SET password=? WHERE id=?", (hashedNewPassword, g.user.id))
    session.clear()
    return json.dumps({"result": "success"})
