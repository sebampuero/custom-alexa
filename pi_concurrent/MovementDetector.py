import threading
import logging
import socket
from utils.email_sender import send_email
from utils.config import ConfigHandler
logger = logging.getLogger(__name__)
import paho.mqtt.client as mqtt

HOST = "localhost"
PORT = 1883
NO_MOVEMENT_THRESHOLD = 30 * 60 * 2 # 20 minutes * 2, because data is sent every 0.5 seconds
TOPIC = "mqtt/distance"

class MovementDetector(threading.Thread):
    '''
    Receives data from an HC-SR04 ultrasonic sensor about the distance in the room. If the distance shortens,
    it means it detected movement, therefore, the heater config has the information that someone is at home.
    '''

    def __init__(self) -> None:
        super().__init__(daemon=True, name="MovementDetector")
        self.counter = 0
        self.movement_inside_detected_already = False

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to MQTT broker with result code: " + str(rc))
        client.subscribe(TOPIC)

    def on_message(self, client, userdata, msg):
        logger.debug("Message: " + msg.payload.decode())
        threshold = 0
        sensor_config = ConfigHandler().open_config()['movement_detector']
        dist = int(msg.payload.decode().split(',')[0])
        sensor_id = msg.payload.decode().split(',')[1]
        if sensor_id == sensor_config['bed_sensor_id']:
            threshold = sensor_config['bed_sensor_threshold']
        elif sensor_id == sensor_config['desk_sensor_id']:
            threshold = sensor_config['desk_sensor_threshold']
        if  dist <= threshold:
            self.counter = 0
            if not self.movement_inside_detected_already:
                plug_config = ConfigHandler().open_config()
                plug_config['heater']['at_home'] = True
                ConfigHandler().write_config(plug_config)
                self.movement_inside_detected_already = True
                logger.info(f"Movement detected at home. Distance: {dist} threshold: {threshold}")
        self.counter += 1
        if self.counter == NO_MOVEMENT_THRESHOLD:
            plug_config = ConfigHandler().open_config()
            plug_config['heater']['at_home'] = False
            ConfigHandler().write_config(plug_config)
            logger.info(f"No more movement detected, not at home. Distance: {dist} threshold: {threshold}")
            send_email(f"Nadie en casa, 0 movimiento detectado.")
            self.movement_inside_detected_already =  False

    def run(self) -> None:
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(HOST, PORT, 60)
        logger.info("Connected to MQTT Broker {0}:{1}".format(HOST, PORT))
        client.loop_forever()
        
