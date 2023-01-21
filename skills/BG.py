from skills.Skill import Skill
from utils.speak import say_text
from utils.config import open_config,write_config
from utils.time_utils import seconds_to_human_readable, minutes_to_seconds
import requests
from datetime import datetime
import re, os
import typing
import logging

logger = logging.getLogger(__name__)


class BG(Skill):

    DEACTIVATE_VOICE_ALARM = "apaga alarma de azúcar"
    ACTIVATE_VOICE_ALARM = "enciende alarma de azúcar"
    LAST_BG_VALUE = "último azúcar"
    VOICE_ALARM_PAUSE = r"pausa (de )?alarmas por (\d{2,3}) (minutos|segundos)"

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

    def trigger(self, transcript) -> typing.Tuple[bool, str]:
        bg_config = open_config()
        if BG.DEACTIVATE_VOICE_ALARM in transcript:
            say_text("Desactivando alarmas de azúcar por voz")
            bg_config['bg']['voice_alert'] = 0
            write_config(bg_config)
            return True, BG.DEACTIVATE_VOICE_ALARM
        elif BG.ACTIVATE_VOICE_ALARM in transcript:
            say_text("Activando alarmas de azúcar por voz")
            bg_config['bg']['voice_alert'] = 1
            write_config(bg_config)
            return True, BG.ACTIVATE_VOICE_ALARM
        elif transcript == BG.LAST_BG_VALUE:
            response = requests.request('GET', BG.BASE_URL + f"entries.json?token={BG.JWT}")
            response = response.json()
            bg_level = response[0]['sgv']
            tendency = response[0]['direction']
            ts = response[0]['date'] / 1000
            seconds_delta = int(datetime.now().timestamp() - ts)
            human_time = seconds_to_human_readable(seconds_delta)
            say_text(f"{bg_level} {BG.TENDENCY_MAP[tendency]} hace {human_time}")
            logger.info(f"Human time was read as: {human_time}")
            return True, BG.LAST_BG_VALUE
        elif re.search(BG.VOICE_ALARM_PAUSE, transcript):
            pause_time = int(re.search(BG.VOICE_ALARM_PAUSE, transcript).group(2))
            time_unit = re.search(BG.VOICE_ALARM_PAUSE, transcript).group(3)
            pause_time_ts = minutes_to_seconds(pause_time) + int(datetime.now().timestamp()) \
                if time_unit == "minutos" else pause_time + int(datetime.now().timestamp())
            bg_config['bg']['voice_alerts_pause_ts'] = pause_time_ts
            write_config(bg_config)
            say_text(f"Pausa de alertas por {pause_time} {time_unit}")
            return True, BG.VOICE_ALARM_PAUSE
        return False, transcript