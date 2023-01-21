from persistence.operations import *
from utils.speak import say_text
from datetime import datetime
from utils.email_sender import send_email
import logging

logger = logging.getLogger(__name__)



MARGIN = 200 # seconds
TWELVE_HOURS = 43200
ONE_HOUR = 3600
FIFTEEN_MINUTES = 900

def lookup_closest_remider():
    try:
        logger.info("Looking up reminders")
        current_ts = int(datetime.now().timestamp())
        reminders_list_tuple = get_reminders() # [ (reminder, timestamp) ... ]
        for rem_tuple in reminders_list_tuple:
            reminder_ts = int(rem_tuple[1])
            actual_reminder = rem_tuple[0]
            if reminder_ts - current_ts < 0:
                logger.info(f"Deleting reminder on past {actual_reminder}")
                delete_top_reminder()
                continue
            if reminder_ts - current_ts <= TWELVE_HOURS + MARGIN:
                if (reminder_ts - TWELVE_HOURS - MARGIN < current_ts) and (reminder_ts - TWELVE_HOURS + MARGIN > current_ts):
                    say_text(f"En 12 horas: {actual_reminder}")
                elif (reminder_ts - ONE_HOUR - MARGIN < current_ts) and (reminder_ts - ONE_HOUR + MARGIN > current_ts):
                    say_text(f"En 1 hora: {actual_reminder}")
                elif (reminder_ts - FIFTEEN_MINUTES - MARGIN < current_ts) and (reminder_ts - FIFTEEN_MINUTES + MARGIN > current_ts):
                    say_text(f"{actual_reminder} en 15 minutos")
                    send_email(f"{actual_reminder} en 15 minutos")
                    delete_top_reminder()
            else:
                break
    except Exception as e:
        logger.error(f"{e} while looking up reminders", exc_info=True)
