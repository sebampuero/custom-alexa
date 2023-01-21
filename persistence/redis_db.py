import redis
import typing
import logging
from operator import itemgetter 

logger = logging.getLogger(__name__)


HOST = "localhost"
PORT = 6379

r = redis.Redis(host=HOST, port=PORT, db=0, charset="utf-8", decode_responses=True)

def delete_key(key):
    r.delete(key)

def save_avg_weight(weight):
    r.rpush('weight_avg', weight)
    weight_avgs_list = weight_avgs()
    return weight_avgs_list[len(weight_avgs_list) - 1]

def save_weight(weight):
    r.rpush("weight", weight)
    return get_last_entry_from_weight_list()

def save_time_of_last_entry(timestamp):
    r.set('last_entry_time', timestamp)
    return r.get('last_entry_time')

def save_last_week_entry_time(timestamp):
    r.set('last_week_entry_time', timestamp)
    return r.get('last_week_entry_time')

def get_last_entry_time():
    return r.get('last_entry_time')

def get_last_week_entry_time():
    return r.get('last_week_entry_time')

def get_last_entry_from_weight_list():
    return r.lrange("weight", -1, -1)

def weight_avgs():
    return r.lrange('weight_avg', 0, -1)

def delete_last_from_weight_list():
    r.rpop("weight")
    return True

def get_last_entries_from_list(num_of_entries):
    if num_of_entries < 1:
        return None
    return r.lrange("weight", int(f'-{num_of_entries}'), -1)

def save_reminder(timestamp, reminder_text):
    r.zadd("reminders", {reminder_text: int(timestamp)})

def get_reminders() -> list:
    return r.zrange("reminders", 0, -1, withscores=True)

def delete_top_reminder():
    return r.zpopmin("reminders", count=1)

def remove_last_reminder(last_reminder_key):
    return r.zrem("reminders", last_reminder_key)

def remove_reminder_like(to_remove: str) -> typing.Tuple[str, str]:
    all_reminders = get_reminders()
    for reminder, scheduled_time in all_reminders:
        if to_remove in reminder.strip():
            logger.debug(f"Deleting reminder {reminder}")
            r.zrem("reminders", reminder)
            return reminder, str(scheduled_time)
    return "", "0"

def save_kv_pair_of_hashname(key: str, name: str, val: str):
    r.hset(name, key=key, value=val)

def get_kv_pair_of_hashname(key: str, name: str) -> str:
    return r.hget(name, key)