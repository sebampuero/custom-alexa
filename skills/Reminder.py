from skills.Skill import Skill
import typing
from utils.speak import say_text
from persistence.operations import *
import dateparser
import typing
import re
from dateparser_data.settings import default_parsers
from datetime import datetime

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Reminder(Skill):

    REMINDER = r"recuérdame|hazme acordar"
    REM_LAST_REMINDER = r"(elimina|borra) último recordatorio"
    REM_REMINDER = r"(elimina|borra) recordatorio [a-z]*"
    WHATS_NEXT_REMINDER = "próximo recordatorio"

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__last_stored_reminder = ""
        self.__settings = {
            "DEFAULT_LANGUAGES": ["es"],
            "PREFER_DATES_FROM": "future"
        }

    def __split_transcript(self, transcript: str) -> typing.Tuple[str, str]:
        phrased_date = transcript.split(re.search(Reminder.REMINDER, transcript).group(0))[0]
        reminder = transcript.split(re.search(Reminder.REMINDER, transcript).group(0))[1]
        return phrased_date.strip(), reminder.strip()

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if re.search(Reminder.REMINDER, transcript):
            phrased_date, actual_reminder = self.__split_transcript(transcript)
            parsed_date = dateparser.parse(phrased_date, settings=self.__settings)
            if parsed_date:
                timestamp = parsed_date.timestamp()
                if int(timestamp) < int(datetime.now().timestamp()):
                    say_text("Imposible guardar recordatorio que esta en el pasado")
                    return True, Reminder.REMINDER
                if actual_reminder == "":
                    return True, Reminder.REMINDER
                say_text(f'Guardado para {phrased_date}, {actual_reminder}')
                save_reminder(timestamp, actual_reminder)
                self.__last_stored_reminder = actual_reminder
                logger.info(f"Reminder: {phrased_date} on {parsed_date}")
            else:
                say_text("No entendí la fecha del recordatorio")
            return True, Reminder.REMINDER
        elif re.match(Reminder.REM_LAST_REMINDER, transcript):
            if self.__last_stored_reminder:
                deleted_reminders = delete_last_reminder(self.__last_stored_reminder)
                if deleted_reminders == 1:
                    say_text(f"Recordatorio {self.__last_stored_reminder} eliminado")
                    return True, Reminder.REM_LAST_REMINDER
        elif transcript == Reminder.WHATS_NEXT_REMINDER:
            next_reminder = get_last_reminder()
            if next_reminder:
                say_text(f"Siguiente recordatorio {next_reminder}")
                return True, Reminder.WHATS_NEXT_REMINDER
            say_text("No hay recordatorios pendientes")
            return True, Reminder.WHATS_NEXT_REMINDER
        elif re.match(Reminder.REM_REMINDER, transcript):
            to_remove = transcript.split(' recordatorio ')[1]
            removed_reminder, scheduled_time = remove_reminder_like(to_remove)
            if not removed_reminder == "":
                say_text(f"{removed_reminder} eliminado")
                return True, Reminder.REM_REMINDER
            say_text(f"No se encontró algún recordatorio con la palabra {to_remove}")
            return True, Reminder.REM_REMINDER
        return False, transcript