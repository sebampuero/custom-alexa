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
            os.system("sudo etherwake -i wlan0 9C:6B:00:15:13:F9")
            return True
        elif re.match(Computer.TURN_OFF_PC, transcript):
            print("Turning off pc")
            os.system("sudo net rpc -S PCMASTERRACE -U shutdowner\%sexoduro shutdown -t 1 -f")#uses samba common package
            return True
        return False
