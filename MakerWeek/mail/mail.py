import smtplib
import email

EMAIL_USERNAME="M4k3rW33d@gmail.com"
EMAIL_PASSWORD="rEenkwqwJ6mggekxnW3hqq0wDDzEO4"
smtp=None

def emailInit():
    global smtp
    smtp=smtplib.SMTP_SSL("smtp.gmail.com")
    status_code, status_msg=smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    print(status_code, ' ', status_msg)
    if status_code!=235:
        raise LoginFailed()

def sendEmail(toAddress, subject, msg):
    global smtp
    print(smtp)
    while smtp is None:
        try:
            emailInit()
        except LoginFailed:
            pass
    content=email.message.Message()
    content.add_header("From", EMAIL_USERNAME)
    content.add_header("To", toAddress)
    content.add_header("Subject", subject)
    content.set_payload(msg, charset="utf-8")
    smtp.send_message(content)

def emailShutdown():
    global smtp
    smtp.quit()


class LoginFailed(Exception):
    pass
