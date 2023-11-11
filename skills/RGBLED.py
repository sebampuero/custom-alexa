import os, time, typing
from skills.Skill import Skill

class RGBLED(Skill):

    TURN_ON_OFF_RGB = "luces"
    BRIGHTNESS_UP = "brillo abajo"
    BRIGHTNESS_DOWN = "brillo arriba"
    BLUE_LED = "luces azul"
    GREEN_LED = "luces verde"
    RED_LED = "luces rojo"
    NEON_BLUE_LED = "luces azul neón"
    DARK_PURPLE_LED = "luces lila oscuro"
    AQUA_LED = "luces azul agua"
    YELLOW_LED = "luces amarillo"

    def trigger(self, transcript: str, intent: dict = None) -> bool:
        if transcript == RGBLED.TURN_ON_OFF_RGB:
            os.system('irsend SEND_ONCE rgbled KEY_F1')
            return True
        elif transcript == RGBLED.BRIGHTNESS_UP:
            for i in range(0, 3):
                os.system('irsend SEND_ONCE rgbled KEY_F4')
                time.sleep(0.2)
            return True
        elif transcript == RGBLED.BRIGHTNESS_DOWN:
            for i in range(0, 3):
                os.system('irsend SEND_ONCE rgbled KEY_F3')
                time.sleep(0.2)
            return True
        elif transcript == RGBLED.BLUE_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F6')
            return True
        elif transcript == RGBLED.GREEN_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F7')
            return True
        elif transcript == RGBLED.RED_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F8')
            return True
        elif transcript == RGBLED.NEON_BLUE_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F10')
            return True
        elif transcript == RGBLED.DARK_PURPLE_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F14')
            return True
        elif transcript == RGBLED.AQUA_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F17')
            return True
        elif transcript == RGBLED.YELLOW_LED:
            os.system('irsend SEND_ONCE rgbled KEY_F24')
            return True
        return False