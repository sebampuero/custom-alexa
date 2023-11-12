from skills.Skill import Skill
import typing
import re
import logging
from utils.speak import say_text
from utils.time_utils import todays_timestamp, seconds_to_human_readable
from persistence.operations import get_attr_of
from utils.config import ConfigHandler

logger = logging.getLogger(__name__)


class Heater(Skill):

    def __update_temp(self, min_or_max: str, transcript: str) -> None:
        heater_conf = ConfigHandler().open_config()
        temp = re.search(r'\d{2}((,| coma )\d{1,2})?', transcript).group(0) # search for 20,4 or 20 or 20 coma 4
        if "coma" or ',' in temp:
            temp = float(temp.replace(' coma ', '.').replace(',', '.'))
        heater_conf['heater'][min_or_max] = temp
        ConfigHandler().write_config(heater_conf)
        min_or_max_text = 'máxima' if min_or_max == 'max_temp' else 'mínima'
        say_text(f"Temperatura {min_or_max_text} puesta en {temp} grados.")

    def trigger(self, transcript: str, intent: dict) -> bool:
        if 'HeaterTime' in intent:
            if 'hoy' in transcript:
                today_time_seconds = get_attr_of("total_seconds", f"heater:{todays_timestamp()}")
                if today_time_seconds:
                    say_text(seconds_to_human_readable(int(today_time_seconds)))
                else:
                    say_text("El calefactor no se ha prendido hoy.")
                return True
            days = int(re.search(r'\d{1,2}', transcript).group(0))
            real_days = days
            all = 0
            for i in range(0,days):
                ts = todays_timestamp() - i * 86400
                total = get_attr_of("total_seconds", f"heater:{ts}")
                all += int(total) if total else 0
                if not total:
                    days -= 1
            say_text(f"Promedio últimos {real_days} días: {seconds_to_human_readable(int(all/days))}")
            return True
        elif 'HeaterTemperature' in intent and 'HeaterTemperatureValues' in intent:
            if intent['HeaterTemperatureValues'] == 'mínima':
                self.__update_temp('min_temp', transcript)
                return True
            self.__update_temp('max_temp', transcript)
            return True
        return False