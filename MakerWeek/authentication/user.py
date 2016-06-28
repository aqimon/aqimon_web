import string

from MakerWeek.database.database import User


def _getHashesPassword(username):
    with getDB() as cursor:
        cursor.execute("SELECT id, password FROM user WHERE username=?", (username,))
        row = cursor.fetchone()
        if row is None:
            raise UserNotFound
        return row['id'], row['password']


def createNewUser(username, password, email):
    password = password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    with getDB() as cursor:
        cursor.execute("INSERT INTO user(username, password, email) VALUES (?, ?, ?)", (username, password, email))


def getIDFromEmail(email):
    with getDB() as cursor:
        cursor.execute("SELECT * FROM user WHERE email=?", (email,))
        result = cursor.fetchone()
    if result is None:
        raise UserNotFound
    return result['id']


def resetPassword(userID):
    newPassword = _generateRandomPassword(20)
    newPasswordHash = bcrypt.hashpw(newPassword.encode("utf-8"), bcrypt.gensalt())
    with getDB() as cursor:
        cursor.execute("UPDATE user SET password=? WHERE id=?", (newPasswordHash, userID))
    return newPassword


def _generateRandomPassword(length):
    rand = random.SystemRandom()
    letters = string.ascii_letters + string.digits
    return ''.join(rand.choice(letters) for _ in range(length))


def getEmailFromID(userID):
    user = User(userID)
    return user.email


class LoginFailed(Exception):
    pass


class UserNotFound(Exception):
    pass
