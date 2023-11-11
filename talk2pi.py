import logging
from logging.handlers import RotatingFileHandler
from utils.config import ConfigHandler
#logging.basicConfig(format='%(asctime)s %(message)s', filename=open_config()['log']['output_file'], filemode="w")
from utils.speak import say_text
import RPi.GPIO as GPIO
from google.cloud import speech
from google.api_core.exceptions import InvalidArgument
from cronjob.scheduler import start_scheduler
from pi_concurrent.MovementDetector import MovementDetector
from IntentManager import IntentManager
import ResumableMicrophoneStream
import time
import typing
import os, importlib
import struct
import pyaudio
import pvporcupine
import nltk

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = RotatingFileHandler(ConfigHandler().open_config()['log']['output_file'], maxBytes=5*1024*1024, backupCount=1)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Google audio recording parameters and config
#16000
SAMPLE_RATE = 44100
CHUNK_SIZE = 4096
#int(SAMPLE_RATE / 10)  # 100ms
READY_TO_TALK_PIN = 27
DID_NOT_UNDERSTAND_PIN = 4
HOT_WORD_SENSIVITY=0.1
CAPTURE_TIMEOUT=30 # seconds

BASE_DIR = ConfigHandler().open_config()['base_dir']

test_mode = False

# Dictionary of skills
skills = {}


client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=SAMPLE_RATE,
    language_code="es-ES",
    max_alternatives=1,
)
streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True
)

for entry in os.scandir(BASE_DIR + "/skills"):
    if (entry.name.endswith(".py") and not entry.name == "Skill.py"): #Abstract class
        skill_name = os.path.splitext(entry.name)[0]
        skill_class = getattr(importlib.import_module(name=f"skills.{skill_name}"), skill_name)
        skills[skill_name] = skill_class(skill_name)


def start_porcupine() -> None:
    # https://picovoice.ai/
    stop_led(READY_TO_TALK_PIN)
    stop_led(DID_NOT_UNDERSTAND_PIN)
    logger.info("Listening for hotword")
    porcupine = pvporcupine.create(access_key=os.getenv("PORCUPINE_KEY"), 
        keyword_paths=[f'{BASE_DIR}/pocurpine/alexa.ppn'], 
        model_path=f'{BASE_DIR}/pocurpine/es_model.pv')
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            porcupine.delete()
            audio_stream.close()
            pa.terminate()
            start_command_capture()

def setup_led(ledpin) -> None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ledpin, GPIO.OUT)

def start_led(ledpin) -> None:
    setup_led(ledpin)
    GPIO.output(ledpin, GPIO.HIGH)


def stop_led(ledpin) -> None:
    setup_led(ledpin)
    GPIO.output(ledpin, GPIO.LOW)


def process_transcript(responses) -> str:
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        if result.is_final:
            return transcript

def get_transcript_from_google() -> str:
    mic_manager = ResumableMicrophoneStream.ResumableMicrophoneStream(
            SAMPLE_RATE, CHUNK_SIZE)
    final_transcript = ""
    start_led(READY_TO_TALK_PIN)
    try:
        audio_generator = mic_manager.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(
            requests=requests, config=streaming_config, timeout=CAPTURE_TIMEOUT
        )
        final_transcript = process_transcript(responses)
    except InvalidArgument:
        logger.error("Timeout reached", exc_info=True)
    except Exception:
        logger.error("Something bad happened", exc_info=True)
    finally:
        mic_manager.terminate()
        return final_transcript
        
def start_command_capture():
    transcript = get_transcript_from_google()
    if not transcript == "":
        logger.info("Processing: %s", transcript)
        process_command_transcript_result(transcript)
    return start_porcupine()

def process_command_transcript_result(transcript: str) -> typing.Tuple[typing.Dict[str, int], str]:
    intent_manager = IntentManager()
    successful = intent_manager.execute_skill_by_intent(transcript)
    if not successful:
        start_led(DID_NOT_UNDERSTAND_PIN)
        say_text(f"No pude entenderte.")

if __name__ == "__main__":
    start_scheduler()
    MovementDetector().start()
    stop_led(READY_TO_TALK_PIN)
    start_led(READY_TO_TALK_PIN)
    time.sleep(2)
    start_porcupine()
    
