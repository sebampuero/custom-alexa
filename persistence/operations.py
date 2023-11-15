import persistence.redis_db as redis_db
import typing

def delete_key(key):
    redis_db.delete_key(key)

def save_weight_avg(avg):
    return redis_db.save_avg_weight(avg)

def save_weight(weight):
    return redis_db.save_weight(weight)

def save_last_entry_time(timestamp):
    return redis_db.save_time_of_last_entry(timestamp)

def save_last_week_entry_time(timestamp):
    return redis_db.save_last_week_entry_time(timestamp)

def get_last_week_entry_time():
    return redis_db.get_last_week_entry_time()

def get_last_entry_time():
    return redis_db.get_last_entry_time()

def get_last_entry():
    return redis_db.get_last_entry_from_weight_list()

def delete_last():
    return redis_db.delete_last_from_weight_list()

def get_last_entries(num_of_entries):
    return redis_db.get_last_entries_from_list(num_of_entries)

def save_reminder(timestamp, reminder_text):
    redis_db.save_reminder(timestamp, reminder_text)

def get_reminders():
    return redis_db.get_reminders()

def delete_top_reminder():
    return redis_db.delete_top_reminder()

def delete_last_reminder(last_reminder_key):
    return redis_db.remove_last_reminder(last_reminder_key)

def get_last_reminder() -> str:
    try:
        return get_reminders()[0][0], get_reminders()[0][1]
    except:
        return None, None

def remove_reminder_like(to_remove: str) -> typing.Tuple[str, str]:
    return redis_db.remove_reminder_like(to_remove)

def get_attr_of(attr: str, name: str) -> str:
    return redis_db.get_kv_pair_of_hashname(attr, name)

def save_attr_of(attr: str, name: str, val: str):
    redis_db.save_kv_pair_of_hashname(attr, name, val)