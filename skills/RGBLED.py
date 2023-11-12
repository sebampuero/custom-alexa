import os, time, typing, re
from skills.Skill import Skill

class RGBLED(Skill):

    BLUE = "azul"
    GREEN = "verde"
    RED = "rojo"
    DARK_PURPLE = "lila"
    YELLOW_LED = "amarillo"

    TURN_ON_OFF = r".*(enciende|encender|prende|prender|apaga|apagar).*"

    def trigger(self, transcript: str, intent: dict) -> bool:
        if re.match(RGBLED.TURN_ON_OFF, intent['RGBLEDVerb']):
            os.system('irsend SEND_ONCE rgbled KEY_F1')
            return True
        elif 'RGBLEDColor' in intent:
            if intent['RGBLEDColor'] == RGBLED.BLUE:
                os.system('irsend SEND_ONCE rgbled KEY_F6')
                return True
            elif intent['RGBLEDColor'] == RGBLED.GREEN:
                os.system('irsend SEND_ONCE rgbled KEY_F7')
                return True
            elif intent['RGBLEDColor'] == RGBLED.RED:
                os.system('irsend SEND_ONCE rgbled KEY_F8')
                return True
            elif intent['RGBLEDColor'] == RGBLED.DARK_PURPLE:
                os.system('irsend SEND_ONCE rgbled KEY_F14')
                return True
            elif intent['RGBLEDColor'] == RGBLED.YELLOW_LED:
                os.system('irsend SEND_ONCE rgbled KEY_F24')
                return True
        return False