import logging
from utils.config import open_config
logging.basicConfig(format='%(asctime)s %(message)s', filename=open_config()['log']['output_file'], filemode="w")
from utils.speak import say_text
import RPi.GPIO as GPIO
from google.cloud import speech
from cronjob.scheduler import start_scheduler
import ResumableMicrophoneStream
import sys
import snowboydecoder
import time
import pygame
import typing
import os, importlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Google audio recording parameters and config
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms
READY_TO_TALK_PIN = 27
HOT_WORD_SENSIVITY=0.18

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


def start_snowboy():
    global snowboy
    stop_led(READY_TO_TALK_PIN)
    snowboy = snowboydecoder.HotwordDetector(model, sensitivity=HOT_WORD_SENSIVITY)
    logger.info("Listening for hotword")
    snowboy.start(detected_callback=start_command_capture, sleep_time=0.1)

def setup_led(ledpin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ledpin, GPIO.OUT)

def start_led(ledpin):
    setup_led(ledpin)
    GPIO.output(ledpin, GPIO.HIGH)


def stop_led(ledpin):
    setup_led(ledpin)
    GPIO.output(ledpin, GPIO.LOW)


def process_transcript(responses):
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript
        if result.is_final:
            logger.info("Transcript: %s result: %s", transcript, str(result))
            return transcript

def open_stream_to_google():
    mic_manager = ResumableMicrophoneStream.ResumableMicrophoneStream(
        SAMPLE_RATE, CHUNK_SIZE)
    audio_generator = mic_manager.generator()
    requests = (
        speech.StreamingRecognizeRequest(audio_content=content)
        for content in audio_generator
    )
    responses = client.streaming_recognize(
        requests=requests, config=streaming_config, timeout=29
    )
    return process_transcript(responses), mic_manager
        

def start_command_capture():
    global snowboy
    snowboy.terminate()
    start_led(READY_TO_TALK_PIN)
    try:
        transcript, mic_manager = open_stream_to_google()
        logger.info("Processing: %s", transcript)
        commands_results_map, skill_if_diverged = process_command_transcript_result(transcript)
        if not skill_if_diverged == "":
            mic_manager.terminate()
            return proceed_with_diverge(skill_if_diverged)
        evaluate_results(commands_results_map)
    except Exception:
        logger.error("Error while transmiting to Google", exc_info=True)
    mic_manager.terminate()
    start_snowboy()

def proceed_with_diverge(skill_module: str):
    if skill_module == skills['Chat'].START_CHAT:
        continous_talk_with_gpt()

def continous_talk_with_gpt():
    while True:
        start_led(READY_TO_TALK_PIN)
        transcript, mic_manager = open_stream_to_google()
        try:
            if transcript == skills['Chat'].STOP_CHAT:
                mic_manager.terminate()
                return start_snowboy()
            stop_led(READY_TO_TALK_PIN)
            skills['Chat'].transmit_to_gpt3(transcript)
        except Exception:
            logger.error("Error while transmiting to Google", exc_info=True)
            return mic_manager.terminate()
        mic_manager.terminate()

def evaluate_results(commands_results_map: typing.Dict[str, int]):
    for command, counter in commands_results_map.items():
        if counter == len(skills.keys()):
            say_text(f"{command} no es un comando")

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
    stop_led(READY_TO_TALK_PIN)
    start_led(READY_TO_TALK_PIN)
    time.sleep(3)
    start_snowboy()
