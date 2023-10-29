import time, schedule
from concurrent.futures import ThreadPoolExecutor
from cronjob.reminder_cronjob import lookup_closest_remider
from cronjob.bg_checker import call_nightscout_api
from cronjob.heater import start_electric_heater
import logging

logger = logging.getLogger(__name__)

INTERVAL_5_MINUTES = 300
INTERVAL_1_MINUTE = 60
INTERVAL_HALF_MINUTE = 30

executor = ThreadPoolExecutor(max_workers=10) 

def run_threaded(job_func):
    executor.submit(job_func)

def five_minute():
    lookup_closest_remider()

def one_minute():
    call_nightscout_api()
    start_electric_heater()

def schedule_the_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    logger.info("Starting scheduler")
    try:
        schedule.every(INTERVAL_5_MINUTES).seconds.do(run_threaded, five_minute)
        schedule.every(INTERVAL_1_MINUTE).seconds.do(run_threaded, one_minute) #TODO: the problem here is that these functions would need to run "in parallel" aka async
        executor.submit(schedule_the_scheduler)
    except Exception as e:
        logger.error(f"{e} while starting scheduler", exc_info=True)
        time.sleep(10.0)
        start_scheduler()
