import boto3

from MakerWeek.config import Config


class SESMail:
    def __init__(self):
        self.config = Config()
        self.sns = boto3.client("ses",
                                aws_access_key_id=self.config.AMAZON_ACCESS_KEY_ID,
                                aws_secret_access_key=self.config.AMAZON_SECRET_ACCESS_KEY,
                                region_name="us-east-1")

    def handler(self, data):
        print(self.sns.send_email(
            Source="notification@e3.tuankiet65.moe",
            Destination={
                'ToAddresses': [
                    data['dst']
                ]
            },
            Message={
                'Subject': {
                    'Data': data['subject']
                },
                'Body': {
                    'Text': {
                        'Data': data['msg']
                    },
                    'Html': {
                        'Data': data['msg']
                    }
                }
            }
        ))


class SESMailVerify:
    def __init__(self):
        self.config = Config()
        self.ses = boto3.client("ses",
                                aws_access_key_id=self.config.AMAZON_ACCESS_KEY_ID,
                                aws_secret_access_key=self.config.AMAZON_SECRET_ACCESS_KEY,
                                region_name="us-east-1")

    def handler(self, data):
        print(self.ses.verify_email_identity(
            EmailAddress=data['email']
        ))
