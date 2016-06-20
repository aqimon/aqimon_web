import random

from MakerWeek.async import async
from MakerWeek.objects import client, event


def burn():
    client.Client.createTable()
    event.Event.createTable()
    return "ok"


def debugMail():
    random.seed()
    tsundereQuote = random.choice([
        "N-No, it's not like I did it for you! I did it because I had freetime, that's all! ┐(￣ヘ￣;)┌",
        "I like you, you idiot!",  # Jackpot m8
        "BAKAAAAAAAAAAAAAAA!!!!! YOU'RE A BAKAAAAAAA!!!!",
        "I'm just here because I had nothing else to do!",
        "Are you stupid?",
        "You're such a slob!",
        "You should be grateful!",
        "You're free anyways, right?",
        "Don't misunderstand, it's not like I like you or anything...",
        "H-Hey....( //・.・ // )",
        "....T-Thanks.....",
        "T-Tch! S-Shut up!",
        "I just had extra, so shut up and take it!",
        "Can you be ANY MORE CLUELESS?",
        "HEY! It's a privilege to even be able to talk to me! You should be honored!",
        "Geez, stop pushing yourself! You're going to get yourself hurt one day, you idiot!"
    ])
    async.sendMail("tuankiet65@gmail.com", "Tsundere quote", tsundereQuote)
    return "xxx"
