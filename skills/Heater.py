from skills.Skill import Skill
import typing
import re
import logging
from utils.speak import say_text
from utils.time_utils import todays_timestamp, seconds_to_human_readable
from persistence.operations import get_attr_of
from utils.config import open_config, write_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Heater(Skill):

    TODAY_HEATER_TIME = r"(tiempo) (del )?(calefactor) (hoy)"
    MIN_TEMP = r"(temperatura )?(mínima)"
    MAX_TEMP = r"(temperatura )?(máxima)"

    def __update_temp(self, min_or_max: str, transcript: str) -> None:
        heater_conf = open_config()
        temp = re.search(r'\d{2}((,| coma )\d{1,2})?', transcript).group(0) # search for 20,4 or 20 or 20 coma 4
        if "coma" or ',' in temp:
            temp = float(temp.replace(' coma ', '.').replace(',', '.'))
        heater_conf['heater'][min_or_max] = temp
        write_config(heater_conf)

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if re.match(Heater.TODAY_HEATER_TIME, transcript):
            today_time_seconds = get_attr_of("total_seconds", f"heater:{todays_timestamp()}")
            if today_time_seconds:
                say_text(seconds_to_human_readable(int(today_time_seconds)))
            else:
                say_text("El calefactor no se ha prendido hoy.")
            return True, Heater.TODAY_HEATER_TIME
        elif re.match(Heater.MIN_TEMP, transcript):
            self.__update_temp('min_temp', transcript)
            return True, Heater.MIN_TEMP
        elif re.match(Heater.MAX_TEMP, transcript):
            self.__update_temp('max_temp', transcript)
            return True, Heater.MAX_TEMP
        return False, transcript