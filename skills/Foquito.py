from skills.Skill import Skill
import typing
import tinytuya
import re, os

class Foquito(Skill):

    TURN_ON = r".*(enciende|encender|prende|prender).*"
    TURN_OFF = r".*(apaga|apagar).*"
    WHITE = "blanco"
    YELLOW = "amarillo"
    RED = "rojo"
    VIOLET = "lila"
    BLUE = "azul"
    GREEN = "verde"
    SLEEP_MODE = 'dormir'
    STUDY_MODE = r".*(estudio|estudiar).*"

    def __setup_tuya(self):
        d = tinytuya.BulbDevice('bf271ed537afe4e631oqwl', '192.168.0.4', os.getenv("BULB_KEY"))
        d.set_version(3.3)
        return d

    def trigger(self, transcript: str, intent: dict = None) -> bool:
        device = self.__setup_tuya()
        if not intent == None: 
            if re.match(Foquito.TURN_ON, intent['BulbVerb']):
                device.turn_on()
                return True
            elif re.match(Foquito.TURN_OFF, intent['BulbVerb']):
                device.turn_off()
                return True
            elif 'BulbColor' in intent:
                if intent['BulbColor'] == Foquito.WHITE:
                    device.set_white(brightness=1000, colourtemp=1000)
                elif intent['BulbColor'] == Foquito.RED:
                    device.set_colour(255, 0, 0)
                elif intent['BulbColor'] == Foquito.VIOLET:
                    device.set_colour(125, 0, 125)
                elif intent['BulbColor'] == Foquito.BLUE:
                    device.set_colour(0, 0, 255)
                elif intent['BulbColor'] == Foquito.GREEN:
                    device.set_colour(0, 255, 0)
                elif intent['BulbColor'] == Foquito.YELLOW:
                    device.set_white(brightness=1000, colourtemp=0)
                return True
            elif 'BulbTemperature' in intent:
                color_temp_val = int(re.search(r"\d{1,3}", transcript).group(0))
                device.set_colourtemp(color_temp_val * 10)
                return True
            elif 'BulbBrightness' in intent:
                percentage = int(re.search(r"\d{1,3}", transcript).group(0))
                device.set_brightness_percentage(percentage)
                return True
            elif 'BulbMode' in intent and 'BulbModes' in intent:
                if intent['BulbModes'] == Foquito.SLEEP_MODE:
                    device.set_brightness_percentage(1)
                    device.set_colourtemp(1)
                elif re.match(Foquito.STUDY_MODE, intent['BulbModes']):
                    device.set_brightness_percentage(100)
                    device.set_white(brightness=1000, colourtemp=1000)
                return True
        return False
