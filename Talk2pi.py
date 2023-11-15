import logging
from logging.handlers import RotatingFileHandler
from utils.config import ConfigHandler
#logging.basicConfig(format='%(asctime)s %(message)s', filename=open_config()['log']['output_file'], filemode="w")
from utils.speak import say_text
from google.cloud import speech
from google.api_core.exceptions import InvalidArgument
from IntentManager import IntentManager
from LedManager import LedManager
import ResumableMicrophoneStream
import time
import os
import struct
import pyaudio # sudo apt-get install portaudio19-dev ?
import pvporcupine

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = RotatingFileHandler(ConfigHandler().open_config()['log']['output_file'], maxBytes=5*1024*1024, backupCount=1)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Talk2pi():
    # Google audio recording parameters and config
    #16000
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 4096
    #int(SAMPLE_RATE / 10)  # 100ms
    CAPTURE_TIMEOUT=30 # seconds

    BASE_DIR = ConfigHandler().open_config()['base_dir']

    def __init__(self, led_manager: LedManager):
        self.client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=Talk2pi.SAMPLE_RATE,
            language_code="es-ES",
            max_alternatives=1,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )
        self.led_manager = led_manager
        self.led_manager.stop_led(LedManager.READY_TO_TALK_PIN)
        self.led_manager.start_led(LedManager.READY_TO_TALK_PIN)
    
    def start(self):
        self._start_porcupine()

    def _start_porcupine(self) -> None:
        # https://picovoice.ai/
        self.led_manager.stop_led(LedManager.READY_TO_TALK_PIN)
        self.led_manager.stop_led(LedManager.DID_NOT_UNDERSTAND_PIN)
        logger.info("Listening for hotword")
        porcupine = pvporcupine.create(access_key=os.getenv("PORCUPINE_KEY"), 
            keyword_paths=[f'{Talk2pi.BASE_DIR}/pocurpine/alexa.ppn'], 
            model_path=f'{Talk2pi.BASE_DIR}/pocurpine/es_model.pv')
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
                self._start_command_capture()

    def _process_transcript(self, responses) -> str:
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            if result.is_final:
                return transcript

    def _get_transcript_from_google(self) -> str:
        mic_manager = ResumableMicrophoneStream.ResumableMicrophoneStream(
                Talk2pi.SAMPLE_RATE, Talk2pi.CHUNK_SIZE)
        final_transcript = ""
        self.led_manager.start_led(LedManager.READY_TO_TALK_PIN)
        try:
            audio_generator = mic_manager.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = self.client.streaming_recognize(
                requests=requests, config=self.streaming_config, timeout=Talk2pi.CAPTURE_TIMEOUT
            )
            final_transcript = self._process_transcript(responses)
        except InvalidArgument:
            logger.error("Timeout reached", exc_info=True)
        except Exception:
            logger.error("Something bad happened", exc_info=True)
        finally:
            mic_manager.terminate()
            return final_transcript
            
    def _start_command_capture(self):
        transcript = self._get_transcript_from_google()
        if not transcript == "":
            logger.info("Processing: %s", transcript)
            self._process_command_transcript_result(transcript)
        self._start_porcupine()

    def _process_command_transcript_result(self, transcript: str):
        intent_manager = IntentManager()
        successful = intent_manager.execute_skill_by_intent(transcript)
        if not successful:
            self.led_manager.start_led(LedManager.DID_NOT_UNDERSTAND_PIN)
            say_text(f"No pude entenderte.")
    
