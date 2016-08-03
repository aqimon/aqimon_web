import boto3

from MakerWeek.config import Config


class SMS:
    def __init__(self):
        self.config = Config()
        self.sns = boto3.client("sns",
                                aws_access_key_id=self.config.AMAZON_ACCESS_KEY_ID,
                                aws_secret_access_key=self.config.AMAZON_SECRET_ACCESS_KEY,
                                region_name="ap-southeast-1")
        print(self.sns.set_sms_attributes(
            attributes={
                "MonthlySpendLimit": "5",
                "DefaultSenderID": "MakerWeek",
                "DefaultSMSType": "Promotional"
            }
        ))

    def handler(self, data):
        if data['dst'][0] == '+':
            data['dst'] = data['dst'][1:]
        if 'transactional' in data:
            msgAttr = {
                "AWS.SNS.SMS.SMSType": {
                    "DataType": "String",
                    "StringValue": "Transactional"
                }
            }
        else:
            msgAttr = {}
        print(self.sns.publish(
            PhoneNumber=data['dst'],
            Message=data['msg'],
            MessageAttributes=msgAttr
        ))
