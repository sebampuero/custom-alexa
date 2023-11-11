from skills.Skill import Skill
from utils.speak import say_text
from utils.config import ConfigHandler
from utils.time_utils import seconds_to_human_readable, minutes_to_seconds
import requests
from datetime import datetime
import re, os
import typing
import logging

logger = logging.getLogger(__name__)


class BG(Skill):

    BASE_URL = os.getenv("NIGHTSCOUT_BASE_URL")
    JWT = os.getenv("NIGHTSCOUT_JWT")

    TENDENCY_MAP = {
        "SingleDown": "Cayendo a más de 3mg por minuto",
        "DoubleDown": "Cayendo muy rápidamente",
        "FortyFiveDown": "Cayendo entre 1 a 3mg por minuto",
        "SingleUp": "Subiendo a más de 3mg por minuto",
        "DoubleUp": "Subiendo muy rápidamente",
        "FortyFiveUp": "Subiendo entre 1 a 3mg por minuto",
        "Flat": "Estable"
    }

    def trigger(self, transcript: str, intent: dict = None) -> bool:
        bg_config = ConfigHandler().open_config()
        response = requests.request('GET', BG.BASE_URL + f"entries.json?token={BG.JWT}")
        response = response.json()
        bg_level = response[0]['sgv']
        tendency = response[0]['direction']
        ts = response[0]['date'] / 1000
        seconds_delta = int(datetime.now().timestamp() - ts)
        human_time = seconds_to_human_readable(seconds_delta)
        say_text(f"{bg_level} {BG.TENDENCY_MAP[tendency]} hace {human_time}")
        logger.info(f"Human time was read as: {human_time}")
        return True