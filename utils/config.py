import json

def open_config():
    with open("/home/pi/talk2pi/config.json", 'r') as f:
        return json.loads(f.read())

def write_config(new_config):
    with open("/home/pi/talk2pi/config.json", 'w') as f:
        f.write(json.dumps(new_config, indent=4))

# Implement this after:
#import json
#import threading

#class ConfigHandler:
#    def __init__(self, filename):
#        self.lock = threading.Lock()
#        self.filename = filename

#    def open_config(self):
#        with self.lock:
#            with open(self.filename, 'r') as f:
#                return json.loads(f.read())

#    def write_config(self, new_config):
#        with self.lock:
#            with open(self.filename, 'w') as f:
#                f.write(json.dumps(new_config, indent=4))

# Create a config handler
#handler = ConfigHandler("/home/pi/talk2pi/config.json")

# Use it from multiple threads
#def worker():
    # This will be run in a separate thread#
#    config = handler.open_config()
#    config['new_key'] = 'value'
#    handler.write_config(config)

# Start a worker thread
#thread = threading.Thread(target=worker)
#thread.start()

# In the main thread, modify the config as well
#config = handler.open_config()
#config['another_key'] = 'value'
#handler.write_config(config)

# Wait for the worker thread to finish
#thread.join()