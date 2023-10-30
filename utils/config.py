import threading
import json

class ConfigHandler:
    _instance = None  # Private class variable to store the singleton instance
    FILENAME = "/home/pi/talk2pi/config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
            cls._instance.lock = threading.Lock()
        return cls._instance

    def open_config(self):
        with self.lock:
            with open(self.FILENAME, 'r') as f:
                return json.loads(f.read())

    def write_config(self, new_config):
        with self.lock:
            with open(self.FILENAME, 'w') as f:
                f.write(json.dumps(new_config, indent=4))