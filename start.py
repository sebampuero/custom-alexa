from cronjob.scheduler import start_scheduler
from Talk2pi import Talk2pi
from LedManager import LedManager
from pi_concurrent.MovementDetector import MovementDetector
import time

if __name__ == "__main__":
    start_scheduler()
    MovementDetector().start()
    led_manager = LedManager()
    talk2pi = Talk2pi(led_manager)
    time.sleep(2)
    talk2pi.start()