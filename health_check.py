from utils.config import open_config
import logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='/home/pi/health_check.log', filemode="w")
from utils.email_sender import send_email
from datetime import datetime
import re
import subprocess

logger = logging.getLogger(__name__)


OUTPUT_FILE = open_config()['log']['output_file']
TIMESTAMP_PATTERN = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})"
MAX_UNHEALTHY_TIME = 300

#TODO: change to http check, which checks internal endpoint (should check if process is running anyways)

def extract_last_timestamp_of_log():
    with open(OUTPUT_FILE, 'r') as f:
        contents = f.read()
    lines = contents.split('\n')
    for line in lines[::-1]:
        pattern = re.search(TIMESTAMP_PATTERN, line)
        if pattern:
            ts = pattern.group(1)
            return ts

def is_alexa_running():
    process_list = subprocess.run(["ps","aux"], stdout=subprocess.PIPE)
    process_list = process_list.stdout
    python3_proc = subprocess.run(["grep","[/]home/pi/voice_control/talk2pi/talk2pi/talk2pi.py"], stdout=subprocess.PIPE, input=process_list)
    python3_proc = python3_proc.stdout.decode('utf-8').strip()
    return not python3_proc == ""

def check_if_healthy():
    extracted_datetime = extract_last_timestamp_of_log()
    ts = int(datetime.strptime(extracted_datetime, '%Y-%m-%d %H:%M:%S,%f').timestamp())
    now_ts = int(datetime.now().timestamp())
    logger.info("Checking health of Alexa")
    if now_ts - ts > MAX_UNHEALTHY_TIME and is_alexa_running():
        restart = subprocess.run(['bash', f'{open_config()["base_dir"]}/restart.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if restart.returncode == 0:
            send_email("Se reinició a Alexa")
        else:
            send_email(f"Hubo problemas reiniciando a Alexa. {restart.stderr}")

check_if_healthy()
