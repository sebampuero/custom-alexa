from skills.Skill import Skill
import typing
import os
import re

class Computer(Skill):

    TURN_ON_PC = r".*(enciende|encender|prende|prender).*"
    TURN_OFF_PC = r".*(apaga|apagar).*"

    def trigger(self, transcript: str, intent: dict) -> bool:
        if re.match(Computer.TURN_ON_PC, transcript):
            print("Turning on pc")
            os.system("sudo etherwake -i wlan0 60:45:CB:64:2D:03")
            return True
        elif re.match(Computer.TURN_OFF_PC, transcript):
            print("Turning off pc")
            os.system("sudo net rpc -S 192.168.0.25 -U shutdowner\%sexoduro shutdown -t 1 -f")#uses samba common package
            return True
        return False
