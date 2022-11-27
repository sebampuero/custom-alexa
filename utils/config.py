import json

def open_config():
    with open("/home/pi/talk2pi/config.json", 'r') as f:
        return json.loads(f.read())

def write_config(new_config):
    with open("/home/pi/talk2pi/config.json", 'w') as f:
        f.write(json.dumps(new_config, indent=4))
