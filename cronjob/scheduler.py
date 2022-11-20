import threading, time, schedule
from cronjob.reminder_cronjob import lookup_closest_remider
from cronjob.bg_checker import call_nightscout_api
from cronjob.heater import start_electric_heater
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


INTERVAL_5_MINUTES = 300
INTERVAL_1_MINUTE = 60
INTERVAL_HALF_MINUTE = 30

def run_continuously(scheduler, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                logger.info(f"Checking pending schedulers on Thread {threading.get_ident()}")
                scheduler.run_pending()
                time.sleep(interval)
            scheduler.cancel_job()

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def five_minute():
    lookup_closest_remider()

def one_minute():
    call_nightscout_api()
    start_electric_heater()

def start_scheduler():
    logger.info("Starting scheduler")
    scheduler1 = schedule.Scheduler()
    scheduler2 = schedule.Scheduler()
    stop_run_continuously = run_continuously(scheduler1, interval=INTERVAL_5_MINUTES)
    stop_run_continuously2 = run_continuously(scheduler2, interval=INTERVAL_1_MINUTE)
    try:
        scheduler1.every(INTERVAL_5_MINUTES).seconds.do(five_minute)
        scheduler2.every(INTERVAL_1_MINUTE).seconds.do(one_minute)
    except Exception as e:
        logger.error(f"{e} while starting scheduler", exc_info=True)
        stop_run_continuously.set()
        stop_run_continuously2.set()
        time.sleep(10.0)
        start_scheduler()
