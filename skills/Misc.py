from skills.Skill import Skill
from utils.speak import say_text
import typing

class Misc(Skill):

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if transcript == 'nada':
            say_text('Ok')
            return True, 'nada'
        return False, transcript
