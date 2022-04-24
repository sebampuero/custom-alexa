# Import modules
import boto3
from botocore.exceptions import ClientError
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

def send_email(text):
    try:
        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=text,
            Subject='Mensaje de Alexa'
        )
    except ClientError:
        logger.error(f"Could not send email {text}", exc_info=True)
    except Exception as e:
        logger.error("Unknown error", exc_info=True)
