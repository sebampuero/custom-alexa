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
            messages = []
            messages.append({"role": "user", "content": question})
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1
            )
            logger.info(str(response))
            say_text(response['choices'][0]['message']['content'])
            return True, GPT.QA
        return False, transcript
