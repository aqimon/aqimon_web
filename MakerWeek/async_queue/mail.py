import email.mime.text
import smtplib


##
## Yeah, I know I shouldn't use Gmail, but I'm too freaking lazy to implement SES
##

class Mail:
    def __init__(self):
        self.EMAIL_USERNAME = "M4k3rW33d@gmail.com"
        self.EMAIL_PASSWORD = "rEenkwqwJ6mggekxnW3hqq0wDDzEO4"
        self._login()

    def _login(self):
        success = False
        while not success:
            self.smtp = smtplib.SMTP_SSL("smtp.gmail.com")
            status_code, status_msg = self.smtp.login(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
            success = (status_code == 235)

    def handler(self, data):
        self._sendMail(data["dst"], data["subject"], data["msg"])

    def _sendMail(self, dst, subject, msg):
        content = email.mime.text.MIMEText(msg, "html", "utf-8")
        content["From"] = self.EMAIL_USERNAME
        content["To"] = dst
        content["Subject"] = subject
        success = False
        while not success:
            try:
                self.smtp.sendmail(self.EMAIL_USERNAME, dst, content.as_string())
            except Exception:
                self._login()
            else:
                success = True
