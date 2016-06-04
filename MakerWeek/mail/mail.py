import email.mime.text
import smtplib

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
    content = email.mime.text.MIMEText(msg, "html", "utf-8")
    content["From"] = EMAIL_USERNAME
    content["To"] = toAddress
    content["Subject"] = subject
    smtp.sendmail(EMAIL_USERNAME, toAddress, content.as_string())

def emailShutdown():
    global smtp
    smtp.quit()


class LoginFailed(Exception):
    pass
