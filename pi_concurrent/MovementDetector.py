import threading
import logging
import socket
from utils.email_sender import send_email
from utils.config import open_config, write_config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HOST = "0.0.0.0"
PORT = 9000
NO_MOVEMENT_THRESHOLD = 30 * 60 * 2 # 20 minutes * 2, because data is sent every 0.5 seconds

class MovementDetector(threading.Thread):
    '''
    Receives UDP data from an HC-SR04 ultrasonic sensor about the distance in the room. If the distance shortens,
    it means it detected movement, therefore, the heater config has the information that someone is at home.
    '''

    def __init__(self) -> None:
        super().__init__(daemon=True, name="MovementDetector")
        self.counter = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((HOST, PORT))
        logger.info("Listening on {0}:{1}_{2}".format(HOST, PORT, MovementDetector.name))
        self.movement_inside_detected_already = False

    def run(self) -> None:
        threshold = 0
        while True:
            sensor_config = open_config()['movement_detector']
            dist, address = self.s.recvfrom(4)
            if address[0] == sensor_config['bed_sensor_ip']:
                threshold = sensor_config['bed_sensor_threshold']
            elif address[0] == sensor_config['desk_sensor_ip']:
                threshold = sensor_config['desk_sensor_threshold']
            dist = int.from_bytes(dist, byteorder='big')
            if  dist <= threshold:
                self.counter = 0
                if not self.movement_inside_detected_already:
                    plug_config = open_config()
                    plug_config['heater']['at_home'] = True
                    write_config(plug_config)
                    self.movement_inside_detected_already = True
                logger.info(f"Movement detected at home. Distance: {dist} threshold: {threshold}")
            self.counter += 1
            if self.counter == NO_MOVEMENT_THRESHOLD:
                plug_config = open_config()
                plug_config['heater']['at_home'] = False
                write_config(plug_config)
                logger.info(f"No more movement detected, not at home. Distance: {dist} threshold: {threshold}")
                send_email(f"Nadie en casa, 0 movimiento detectado.")
                self.movement_inside_detected_already =  False
        
