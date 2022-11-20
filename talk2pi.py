import logging
from logging.handlers import TimedRotatingFileHandler
from utils.config import open_config
#logging.basicConfig(format='%(asctime)s %(message)s', filename=open_config()['log']['output_file'], filemode="w")
from utils.speak import say_text
import RPi.GPIO as GPIO
from google.cloud import speech
from google.api_core.exceptions import InvalidArgument
from cronjob.scheduler import start_scheduler
from pi_concurrent.MovementDetector import MovementDetector
import ResumableMicrophoneStream
import sys
import snowboydecoder
import time
import pygame
import typing
import os, importlib

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = TimedRotatingFileHandler(open_config()['log']['output_file'], when='d')
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

os.putenv('SDL_VIDEODRIVER', 'dummy')
pygame.init()

BASE_DIR = open_config()['base_dir']

test_mode = False

# Snowboy object placeholder
snowboy = None

# Dictionary of skills
skills = {}

# Path to the hotword model file
try:
    model = sys.argv[1]
except IndexError:
    print("Testing mode")
    test_mode = True  

if not test_mode:
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

for entry in os.scandir(BASE_DIR + "skills"):
    if (entry.name.endswith(".py") and not entry.name == "Skill.py"): #Abstract class
        skill_name = os.path.splitext(entry.name)[0]
        skill_class = getattr(importlib.import_module(name=f"skills.{skill_name}"), skill_name)
        skills[skill_name] = skill_class(skill_name)


def start_snowboy() -> None:
    global snowboy
    stop_led(READY_TO_TALK_PIN)
    stop_led(DID_NOT_UNDERSTAND_PIN)
    snowboy = snowboydecoder.HotwordDetector(model, sensitivity=HOT_WORD_SENSIVITY)
    logger.info("Listening for hotword")
    snowboy.start(detected_callback=start_command_capture)

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
    global snowboy
    snowboy.terminate()
    start_led(READY_TO_TALK_PIN)
    transcript = get_transcript_from_google()
    if not transcript == "":
        logger.info("Processing: %s", transcript)
        commands_results_map, skill_if_diverged = process_command_transcript_result(transcript)
        if not skill_if_diverged == "":
            return proceed_with_diverge(skill_if_diverged)
        evaluate_results(commands_results_map)
    return start_snowboy()
        
def proceed_with_diverge(skill_module: str):
    if skill_module == skills['Chat'].START_CHAT:
        continous_talk_with_gpt()

def continous_talk_with_gpt():
    while True:
        start_led(READY_TO_TALK_PIN)
        transcript = get_transcript_from_google()
        if transcript == skills['Chat'].STOP_CHAT or transcript == "":
            return start_snowboy()
        stop_led(READY_TO_TALK_PIN)
        skills['Chat'].transmit_to_gpt3(transcript)

def evaluate_results(commands_results_map: typing.Dict[str, int]):
    for command, counter in commands_results_map.items():
        if counter == len(skills.keys()):
            start_led(DID_NOT_UNDERSTAND_PIN)
            say_text(f"No entendí {command}")

def process_command_transcript_result(transcript: str) -> typing.Tuple[typing.Dict[str, int], str]:
    transcript = transcript.lower()
    commands = transcript.split(' y ')
    bad_commands_counter = dict()
    for name, skill in skills.items():
        for a_command in commands:
            try:
                successful, command = skill.trigger(a_command)
            except Exception:
                logger.error("Ejecutando skill", exc_info=True)
                say_text("Hubo un error ejecutando el comando")
            if not successful:
                if a_command not in  bad_commands_counter.keys():
                    bad_commands_counter[a_command] = 1
                else:
                    bad_commands_counter[a_command] += 1
            if command == skills['Chat'].START_CHAT: #TODO: delegate in other function if this grows
                return bad_commands_counter, skills['Chat'].START_CHAT
    return bad_commands_counter, ""

if not test_mode:
    start_scheduler()
    MovementDetector().start()
    stop_led(READY_TO_TALK_PIN)
    start_led(READY_TO_TALK_PIN)
    time.sleep(2)
    start_snowboy()
