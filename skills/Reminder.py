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


class Reminder(Skill):

    REMINDER = r".*(recuérdame|hazme acordar).*"
    REM_LAST_REMINDER = "último"
    REM_REMINDER = r".*(elimina|borra).*"
    REM_NEXT = r".*(siguiente|próximo).*"

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__settings = {
            "DEFAULT_LANGUAGES": ["es"],
            "PREFER_DATES_FROM": "future"
        }

    def __split_transcript(self, transcript: str, verb: str) -> typing.Tuple[str, str]:
        phrased_date = transcript.split(verb)[0].strip()
        reminder = transcript.split(verb)[1].strip()
        return phrased_date, reminder

    def trigger(self, transcript: str, intent: dict) -> bool:
        if re.match(Reminder.REMINDER, intent['ReminderVerb']):
            phrased_date, actual_reminder = self.__split_transcript(transcript, intent['ReminderVerb'])
            parsed_date = dateparser.parse(phrased_date, settings=self.__settings)
            if parsed_date:
                timestamp = parsed_date.timestamp()
                if int(timestamp) < int(datetime.now().timestamp()):
                    say_text("Imposible guardar recordatorio que esta en el pasado")
                    return True
                if actual_reminder == "":
                    return True
                say_text(f'Guardado para {phrased_date}, {actual_reminder}')
                save_reminder(timestamp, actual_reminder)
                logger.info(f"Reminder: {phrased_date} on {parsed_date}")
            else:
                say_text("No entendí la fecha del recordatorio")
            return True
        elif 'ReminderTime' in intent:
            if re.match(Reminder.REM_NEXT, intent['ReminderTime']):
                next_reminder = get_last_reminder()
                if next_reminder:
                    say_text(f"Siguiente recordatorio {next_reminder}")
                    return True
                say_text("No hay recordatorios pendientes")
                return True
        elif re.match(Reminder.REM_REMINDER, intent['ReminderVerb']):
            to_remove = transcript.split(' recordatorio ')[1]
            removed_reminder, scheduled_time = remove_reminder_like(to_remove)
            if not removed_reminder == "":
                say_text(f"{removed_reminder} eliminado")
                return True
            say_text(f"No se encontró algún recordatorio con la palabra {to_remove}")
            return True
        return False