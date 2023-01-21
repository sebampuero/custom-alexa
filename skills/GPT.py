from skills.Skill import Skill
import typing

import os
import openai
import logging
from utils.speak import say_text

openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)


class GPT(Skill):

    QA = "respóndeme"

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        question_phrase = transcript.split(GPT.QA)
        if len(question_phrase) == 2:
            question = question_phrase[1].strip()
            response = openai.Completion.create(
                engine="curie",
                prompt="Q: " + question + "?\nA:",
                temperature=0.7,
                max_tokens=100,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1,
                stop=["\nQ:"]
                )
            actual_response = response.choices[0].text.strip().replace('A: ', '')
            logger.info(str(response))
            say_text(actual_response)
            return True, GPT.QA
        return False, transcript