from skills.Skill import Skill
from utils.speak import say_text
import typing

class Misc(Skill):

    def trigger(self, transcript: str, intent: dict) -> bool:
        if transcript == 'nada':
            say_text('Ok')
            return True
        return False
