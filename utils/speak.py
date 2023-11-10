from subprocess import call
from boto3 import Session
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
import logging
logger = logging.getLogger(__name__)

def say_text(my_text):
    session = Session()
    polly = session.client("polly")
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=my_text, OutputFormat="mp3",
                         VoiceId="Mia", LanguageCode='es-MX')
    except (BotoCoreError, ClientError) as error:
        logger.error(f"Error when using Polly {error}", exc_info=True)
    if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                with open("say.mp3", "wb") as file:
                    file.write(stream.read())
            call(["mpg123", "say.mp3"])
    else:
        logger.error(f"No audio data in stream", exc_info=True)

