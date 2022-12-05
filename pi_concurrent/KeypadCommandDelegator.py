import socket
import threading
import logging
from utils.config import open_config, write_config
from utils.speak import say_text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HOST = "0.0.0.0"
PORT = 9010

MIN_TEMP_CMD = 'A'
MAX_TEMP_CMD = 'B'

class KeypadCommandDelegator(threading.Thread):

    def __init__(self) -> None:
        super().__init__(daemon=True, name="KeypadThread")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((HOST, PORT))
        logger.info("Listening on {0}:{1}_{2}".format(HOST, PORT, KeypadCommandDelegator.name))
        self.stack = []

    def run(self) -> None:
        while True:
            val = self.s.recv(4).decode()
            logger.info(f"Received {val} from keypad")
            if val == 'D':
                self.stack.clear()
            elif val == '#':
                self._evaluate_result()
            else:
                self.stack.append(val)

    def _evaluate_result(self) -> None:
        for idx, val in enumerate(self.stack):
            if not val.isnumeric():
                continue
            cmd = ''.join(self.stack[0:idx])
            if cmd == MIN_TEMP_CMD:
                self.__edit_temp(self.stack[idx:], min=True)
                break
            elif cmd == MAX_TEMP_CMD:
                self.__edit_temp(self.stack[idx:], min=False)
                break
            else:
                say_text(f"{cmd} no es válido")
                break
        self.stack.clear()

    def __edit_temp(self, value: list, min: bool):
        try:
            heater_conf = open_config()
            temp = float(''.join(value).replace('*', '.'))
            if min:
                heater_conf['heater']['min_temp'] = temp
            else:
                heater_conf['heater']['max_temp'] = temp
            write_config(heater_conf)
            logger.info("Saved new temp values")
        except ValueError:
            say_text(f"{''.join(value).replace('*', '.')} no es temperatura válida")

            
