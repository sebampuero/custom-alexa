from skills.Skill import Skill
import typing
import tinytuya
import re, os

class Foquito(Skill):

    TURN_ON = r"(enciende|prende) (la )?(el )?(foco|luz)"
    TURN_OFF = r"apaga (la )?(el )?(luz|foco)"
    WHITE = "blanco"
    YELLOW = "amarillo"
    RED = "rojo"
    VIOLET = "lila"
    BLUE = "azul"
    GREEN = "verde"
    COLOR_TEMP = r"temperatura (del foco|color) \d{1,3}$"
    BRIGHTNESS = r"brillo (de luz )?\d{1,3}$"
    SLEEP_MODE = "modo dormir"

    def __setup_tuya(self):
        d = tinytuya.BulbDevice('bf271ed537afe4e631oqwl', '192.168.0.3', os.getenv("BULB_KEY"))
        d.set_version(3.3)
        return d

    def trigger(self, transcript) -> typing.Tuple[bool, str]:
        device = self.__setup_tuya()
        if re.match(Foquito.TURN_ON, transcript):
            device.turn_on()
            return True, Foquito.TURN_ON
        elif re.match(Foquito.TURN_OFF, transcript):
            device.turn_off()
            return True, Foquito.TURN_OFF
        elif transcript == Foquito.WHITE:
            device.set_white(brightness=1000, colourtemp=1000)
            return True, Foquito.WHITE
        elif transcript == Foquito.YELLOW:
            device.set_white(brightness=1000, colourtemp=0)
            return True, Foquito.YELLOW
        elif re.match(Foquito.BRIGHTNESS, transcript):
            percentage = int(re.search(r"\d{1,3}", transcript).group(0))
            device.set_brightness_percentage(percentage)
            return True, Foquito.BRIGHTNESS
        elif transcript == Foquito.RED:
            device.set_colour(255, 0, 0)
            return True, Foquito.RED
        elif transcript == Foquito.VIOLET:
            device.set_colour(125, 0, 125)
            return True, Foquito.VIOLET
        elif transcript == Foquito.BLUE:
            device.set_colour(0, 0, 255)
            return True, Foquito.BLUE
        elif transcript == Foquito.GREEN:
            device.set_colour(0, 255, 0)
            return True, Foquito.GREEN
        elif re.match(Foquito.COLOR_TEMP, transcript):
            color_temp_val = int(re.search(r"\d{1,3}", transcript).group(0))
            device.set_colourtemp(color_temp_val * 10)
            return True, Foquito.COLOR_TEMP
        elif transcript == Foquito.SLEEP_MODE:
            device.set_brightness_percentage(1)
            device.set_colourtemp(1)
            return True, Foquito.SLEEP_MODE
        return False, transcript
