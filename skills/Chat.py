from skills.Skill import Skill
import typing
import os
import openai
import logging
from utils.speak import say_text

openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Chat(Skill):

    START_CHAT = "hablemos un rato"
    STOP_CHAT = "para la conversación"

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__conversation_history = ""

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if transcript == Chat.START_CHAT:
            say_text("Ok, hablemos")
            return True, Chat.START_CHAT
        return False, transcript
    
    def transmit_to_gpt3(self, text):
        intro = "La siguiente es una conversación con una inteligencia artificial. La inteligencia artificial es amigable aveces.\n\n"
        if self.__conversation_history == "":
            self.__conversation_history = intro + "Humano:" + text + "\nIA:"
        else:
            self.__conversation_history = self.__conversation_history + "\nHumano:" + text + "\nIA:"
        response = openai.Completion.create(
            engine="davinci",
            prompt=self.__conversation_history,
            temperature=0.9,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\n", "\nHumano:", "\nIA:"]
            )
        actual_response = response.choices[0].text.strip()
        actual_response = actual_response.lower().replace('humano:', '').replace('ia:', '')
        self.__conversation_history = self.__conversation_history + actual_response
        say_text(actual_response)