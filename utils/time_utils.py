from datetime import datetime
import time

DAYS_OF_WEEK = {
    0: 'Lunes',
    1: 'Martes',
    2: 'Miércoles',
    3: 'Jueves',
    4: 'Viernes',
    5: 'Sábado',
    6: 'Domingo'
}

DAY_SECONDS = 86400

def todays_timestamp():
    today = datetime.today().strftime('%Y-%m-%d')
    return int(time.mktime(datetime.strptime(today, "%Y-%m-%d").timetuple()))

def is_unix_timestamp(value: int) -> bool:
    value = str(value)
    return len(value) == 10

def seconds_to_minutes(seconds: int) -> int:
    if seconds <= 60:
        return seconds
    return int(seconds / 60)

def minutes_to_seconds(minutes: int) -> int:
    return int(minutes * 60)

def seconds_to_human_readable(seconds: int) -> str:
    minutes = int(seconds / 60)
    parsed_seconds = ""
    if minutes <= 60:
        minutes_txt = f"{minutes} minutos " if minutes > 1 else f"{minutes} minuto"
        rem_seconds = int(seconds % 60)
        seconds_txt = f"{rem_seconds} segundos " if rem_seconds > 1 else f"{rem_seconds} segundo"
        parsed_seconds = f"{minutes_txt} y {seconds_txt}"
    else:
        hours = int(minutes / 60)
        hours_txt = f"{hours} horas " if hours > 1 else f"{hours} hora"
        rem_minutes = int(minutes % 60)
        minutes = f"{rem_minutes} minutos " if rem_minutes > 1 else f"{rem_minutes} minuto"
        parsed_seconds = f"{hours_txt} y {minutes}"
    return parsed_seconds

def remaining_seconds_to_human_readable(future_ts: int) -> str:
    rest_ts = future_ts - int(datetime.now().timestamp())
    div = int(rest_ts/DAY_SECONDS)
    hour = datetime.fromtimestamp(future_ts).hour
    minute = datetime.fromtimestamp(future_ts).minute
    if div == 1:
        return f"mañana a las {hour} y {minute}"
    elif div > 1 and div < 7:
        return f"en {div} días, a las {hour} y {minute}"
    elif div == 0:
        return f"hoy a las {hour} y {minute}"
    return None