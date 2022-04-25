from utils.speak import say_text
from datetime import datetime
from utils.email_sender import send_email
from utils.config import open_config
import requests
import logging
import re, os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DANGER_DOWN = "SingleDown"
SUPER_DANGER_DOWN = "DoubleDown"
LESS_DANGER_DOWN = "FortyFiveDown"
UP_RAPID = "SingleUp"
UP_SLOW = "FortyFiveUp"
TEN_MINUTES = 600
NO_VALUES_DOWN_THRESHOLD = 1200
NO_VALUES_UP_THRESHOLD = 1500
BASE_URL = os.getenv("NIGHTSCOUT_BASE_URL")

active = False

def uploader_active():
    global active
    endpoint = "entries.json"
    response = requests.request('GET', BASE_URL + endpoint).json()
    ts = response[0]['date'] / 1000
    current_ts = datetime.now().timestamp()
    if current_ts - ts < TEN_MINUTES:
        if not active:
            send_email("Valores de azucar reanudados")
        active = True
        return True
    elif current_ts - ts > NO_VALUES_DOWN_THRESHOLD and current_ts - ts < NO_VALUES_UP_THRESHOLD:
        if active:
            send_email("Sin valores de azucar desde hace mas de 20 minutos")
        active = False
        return False

def check_req_ch():
    bg_config = open_config()['bg']
    carbs_req_pattern = r"(\d{1,2}) add.* req w\/in (\d{1,2})m"
    endpoint = "devicestatus.json"
    response = requests.request('GET', BASE_URL + endpoint).json()
    suggest_reason = response[0]['openaps']['suggested']['reason']
    if re.search(carbs_req_pattern, suggest_reason):
        req_carbs = re.search(carbs_req_pattern, suggest_reason).group(1)
        in_minutes = re.search(carbs_req_pattern, suggest_reason).group(2)
        logger.info(f"Required: {req_carbs} in {in_minutes} minutes")
        if int(req_carbs) > 0:
            send_email(f"{req_carbs} ch requeridos en {in_minutes} minutos, chequear APS y comer!")
            if int(datetime.now().timestamp()) > bg_config['voice_alerts_pause_ts']:
                say_text(f"{req_carbs} carbos se necesitan o se entrará pronto en bajada de azúcar")

def check_latest_bg():
    bg_config = open_config()['bg']
    endpoint = "entries.json?find[sgv][$gt]=30"
    response = requests.request('GET', BASE_URL + endpoint).json()
    bg_level = response[0]['sgv']
    tendency = response[0]['direction']
    current_ts = int(datetime.now().timestamp())
    logger.info("BG: %s TENDENCY: %s", str(bg_level), tendency)
    if bg_level <= bg_config["dangerous_for_down2"] and bg_level >= bg_config["dangerous_for_down1"] and (tendency == DANGER_DOWN or tendency == SUPER_DANGER_DOWN):
        if current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f"El azúcar cae muy rápido y está en {bg_level}")
        send_email(f'{bg_level} y {tendency}, para la insulina !!!')
    elif bg_level <= bg_config["semi_dangerous_for_down2"] and bg_level >= bg_config['semi_dangerous_for_down1'] and (tendency == LESS_DANGER_DOWN):
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Azúcar en {bg_level} y bajando, será mejor parar la insulina')
        send_email(f"Bellina con {bg_level} y {tendency}, parar la insulina por un rato")
    elif bg_level <= bg_config["low_th"] and ( tendency == DANGER_DOWN or tendency == LESS_DANGER_DOWN or tendency == SUPER_DANGER_DOWN):
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Belina con valores peligrosos de {bg_level} y tendencia hacia abajo')
        send_email(f'Belina con valores peligrosos de {bg_level} y {tendency}')
    elif bg_level <= bg_config["very_low_th"]:
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Belina en una bajada de azúcar!')
        send_email(f'Belina esta muy baja con {bg_level} y tendencia {tendency}')
    elif bg_level >= bg_config["up_th"]:
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Belina alta con {bg_level}')
        send_email(f'Belina alta con {bg_level} con tendencia {tendency}')

def call_nightscout_api():
    try:
        if uploader_active():
            check_latest_bg()
            check_req_ch()
    except Exception:
        logger.error('While checking bg values', exc_info=True)
