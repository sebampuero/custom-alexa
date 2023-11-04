from skills.Skill import Skill
import os
import typing
import openai
import logging
import asyncio
from gtts import gTTS
from subprocess import call

openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)


class GPT(Skill):

    QA = "respóndeme"

    def _speak(self, chunk: str):
        tts = gTTS(chunk, lang='es')
        tts.save('chunk.mp3')
        call(["mpg123", "chunk.mp3"])

    async def _main(self, messages: dict):
        loop = asyncio.get_event_loop()
        response_generator = await self._get_chat_completion_as_stream(messages)
        buffered_content = ""
        async for response_chunk in response_generator:
            delta = response_chunk["choices"][0]["delta"]
            if "content" in delta:
                buffered_content += delta["content"]
                if delta["content"] == ".":
                    await loop.run_in_executor(None, self._speak, buffered_content)
                    buffered_content = ""

    async def _get_chat_completion_as_stream(self, messages: dict):
        response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1,
                stream=True
            )
        return response

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        question_phrase = transcript.split(GPT.QA)
        if len(question_phrase) == 2:
            question = question_phrase[1].strip()
            messages = []
            messages.append({"role": "user", "content": question})
            asyncio.run(self._main(messages))
            return True, GPT.QA
        return False, transcript
