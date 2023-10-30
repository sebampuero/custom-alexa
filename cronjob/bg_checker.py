from utils.speak import say_text
from datetime import datetime
from dateutil.parser import parse
from utils.email_sender import send_email
from utils.config import ConfigHandler
import requests
import logging
import re, os

logger = logging.getLogger(__name__)


DANGER_DOWN = "SingleDown"
SUPER_DANGER_DOWN = "DoubleDown"
LESS_DANGER_DOWN = "FortyFiveDown"
TEN_MINUTES = 600
CARBS_MIN_THRESH = 15
BASE_URL = os.getenv("NIGHTSCOUT_BASE_URL")
JWT = os.getenv("NIGHTSCOUT_JWT")
BELLINA_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN_BELLINA")
MAX_CH_CHECKS = 8

last_ch_check = 0
last_bg_check = 0
last_ch_required = 0

def check_req_ch():
    global last_ch_check
    carbs_req_pattern = r"(\d{1,2}) add.* req w\/in (\d{1,2})m"
    endpoint = f"devicestatus?token={JWT}"
    response = requests.request('GET', BASE_URL + endpoint).json()
    suggest_reason = response[0]['openaps']['suggested']['reason']
    ts = parse(response[0]['created_at']).timestamp()
    if last_ch_check == ts:
        return
    last_ch_check = ts
    if re.search(carbs_req_pattern, suggest_reason):
        req_carbs = re.search(carbs_req_pattern, suggest_reason).group(1)
        in_minutes = int(re.search(carbs_req_pattern, suggest_reason).group(2))
        if in_minutes <= 15:
            logger.info(f"Required: {req_carbs} in {in_minutes} minutes")
            send_email(f"{req_carbs} ch requeridos en {in_minutes} minutos")
            #send_email(f"{int(int(req_carbs)/2)} ch requeridos en {in_minutes} minutos.", BELLINA_TOPIC_ARN)
                
def check_latest_bg():
    global last_bg_check
    bg_config = ConfigHandler().open_config()['bg']
    endpoint = f"entries.json?token={JWT}"
    response = requests.request('GET', BASE_URL + endpoint).json()
    bg_level = response[0]['sgv']
    tendency = response[0]['direction']
    ts = int(response[0]['date'] / 1000)
    if last_bg_check == ts and response[0]["isValid"]:
        return
    last_bg_check = ts
    current_ts = int(datetime.now().timestamp())
    logger.info("BG: %s TENDENCY: %s", str(bg_level), tendency)
    if bg_level <= bg_config["dangerous_for_down2"] and bg_level >= bg_config["dangerous_for_down1"] and (tendency == DANGER_DOWN or tendency == SUPER_DANGER_DOWN):
        send_email(f'{bg_level} y {tendency}, mucho cuidado!')
    elif bg_level <= bg_config["low_th"] and ( tendency == DANGER_DOWN or tendency == LESS_DANGER_DOWN or tendency == SUPER_DANGER_DOWN):
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Belina con valores peligrosos de {bg_level} y tendencia hacia abajo')
        send_email(f'Belina con valores peligrosos de {bg_level} y {tendency}')
    elif bg_level <= bg_config["very_low_th"]:
        if bg_config['voice_alert'] and current_ts > bg_config['voice_alerts_pause_ts']:
            say_text(f'Belina en una bajada de azúcar!')
        send_email(f'Belina esta muy baja con {bg_level} y tendencia {tendency}')

def call_nightscout_api():
    try:
        check_latest_bg()
        check_req_ch()
    except Exception:
        logger.error('While checking bg values', exc_info=True)
