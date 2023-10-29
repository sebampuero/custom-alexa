import logging
import asyncio
import os
from datetime import datetime
import time
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from utils.time_utils import todays_timestamp
from utils.config import open_config
from utils.time_utils import todays_timestamp, is_unix_timestamp
from persistence.operations import get_attr_of, save_attr_of
import requests #using requests instead of async requests because lazyness

logger = logging.getLogger(__name__)


EMAIL = os.environ.get('MEROSS_EMAIL')
PASSWORD = os.environ.get('MEROSS_PASSWORD')

def start_electric_heater() -> None:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        loop.close()
    except:
        logger.error('While checking heater', exc_info=True)

def outside_operative_hours(config: dict) -> bool:
    now = datetime.now()
    return now.hour >= int(config['non_operative_hours'].split('-')[0]) and now.hour <= int(config['non_operative_hours'].split('-')[1])

async def main():
    plug_config = open_config()['heater']
    indoor_temp = requests.request('GET', "http://192.168.0.10/temp").text
    if not indoor_temp:
        return None
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    manager = MerossManager(http_client=http_api_client)
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss110")
    device = list(filter(lambda plug: plug.name == 'calefactor', plugs))[0]
    await device.async_update()
    if float(indoor_temp) <= plug_config['min_temp'] and not device.is_on() \
            and plug_config['at_home'] and not outside_operative_hours(plug_config) and not plug_config['force_off']:
        logger.info(f"Turning on heater because temp is {indoor_temp}")
        save_start_of_heater()
        await device.async_turn_on()
    elif float(indoor_temp) >= plug_config['max_temp'] and device.is_on():
        logger.info(f"Turning off heater because temp is {indoor_temp}")
        save_end_of_heater_seconds()
        await device.async_turn_off()
    manager.close()
    await http_api_client.async_logout()


def save_start_of_heater():
    '''
    Save the start timestamp of heater. If it was previously shut down by app, add 30 minutes to the total seconds
    because that is the max allowed time set ON for the heater in the Meross app.
    '''
    key = f"heater:{todays_timestamp()}"
    last_start_ts = get_attr_of("start_ts", key)
    try:
        if is_unix_timestamp(int(last_start_ts)): # last time it was shut off via app
            total_seconds = get_attr_of("total_seconds", key) if not None else 0
            total_seconds = int(total_seconds) + 30 * 60
            save_attr_of("total_seconds", key, str(total_seconds))
    except TypeError: # int(last_start_ts) tried casting None to int
        logger.info("First time of day saving heater seconds counter")
        save_attr_of("total_seconds", key, "0")
    finally:
        save_attr_of("start_ts", key, str(int(time.time())))

def save_end_of_heater_seconds():
    '''
    Save the end timestamp of the heater and add the different to total seconds. It takes in account also if the heater
    was turned on the previous day and it needs to be shut off the next day, then the function logs the seconds for the 
    previous day.
    '''
    key = f"heater:{todays_timestamp()}"
    total_seconds = get_attr_of("total_seconds", key)
    if not total_seconds:
        start_ts_of_prev_day = get_attr_of("start_ts", f"heater:{todays_timestamp() - 86400}")
        prev_total_seconds = get_attr_of("total_seconds", f"heater:{todays_timestamp() - 86400}")
        prev_day_total_seconds = int(time.time()) - int(start_ts_of_prev_day) + int(prev_total_seconds)
        save_attr_of("total_seconds", f"heater:{todays_timestamp() - 86400}", str(prev_day_total_seconds))
    else:
        start_ts = get_attr_of("start_ts", key) if not None else 0
        if int(start_ts) == 0:
            return None # heater was started via app
        new_total_seconds = int(time.time()) - int(start_ts) + int(total_seconds)
        save_attr_of("total_seconds", key, str(new_total_seconds))
    save_attr_of("start_ts", key, "0")
