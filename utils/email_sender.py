# Import modules
import boto3
from botocore.exceptions import ClientError
import logging
import os

logger = logging.getLogger(__name__)

MAIN_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

def send_email(text, topic=None):
    try:
        sns_client = boto3.client('sns')
        if topic:
            sns_client.publish(
                TopicArn=topic,
                Message=text,
                Subject='Notificacion de Nightscout'
            )
        else:
            sns_client.publish(
                TopicArn=MAIN_TOPIC_ARN,
                Message=text,
                Subject='Mensaje de Alexa'
            )
    except ClientError:
        logger.error(f"Could not send email {text}", exc_info=True)
    except Exception as e:
        logger.error("Unknown error", exc_info=True)
