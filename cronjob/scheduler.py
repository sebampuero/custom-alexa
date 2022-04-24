import threading, time, schedule, traceback
from cronjob.reminder_cronjob import lookup_closest_remider
from cronjob.bg_checker import call_nightscout_api
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


FIRST_INTERVAL_5_MINS = 300
SECOND_INTERVAL_10_MINS = 600

def run_continuously(scheduler, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                scheduler.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def background_job():
    lookup_closest_remider()
    call_nightscout_api()

def start_scheduler():
    logger.info("Starting scheduler")
    scheduler1 = schedule.Scheduler()
    #scheduler2 = schedule.Scheduler()
    stop_run_continuously = run_continuously(scheduler1, interval=FIRST_INTERVAL_5_MINS)
    #stop_run_continuously2 = run_continuously(scheduler2, interval=SECOND_INTERVAL_10_MINS)
    try:
        scheduler1.every(FIRST_INTERVAL_5_MINS).seconds.do(background_job)
        #scheduler2.every(SECOND_INTERVAL_10_MINS).seconds.do(second_background_job)
    except Exception as e:
        logger.error(f"{e} while starting scheduler", exc_info=True)
        stop_run_continuously.set()
        #stop_run_continuously2.set()
        time.sleep(60.0)
        start_scheduler()
