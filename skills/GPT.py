from skills.Skill import Skill
import os
import typing
import openai
import logging
import asyncio
from utils.speak import say_text

openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)


class GPT(Skill):

    QA = "respóndeme"

    async def _main(self, messages: dict):
        loop = asyncio.get_event_loop()
        response_generator = await self._get_chat_completion_as_stream(messages)
        buffered_content = ""
        async for response_chunk in response_generator:
            delta = response_chunk["choices"][0]["delta"]
            if "content" in delta:
                buffered_content += delta["content"]
                if delta["content"] == ".":
                    await loop.run_in_executor(None, say_text, buffered_content)
                    buffered_content = ""

    async def _get_chat_completion_as_stream(self, messages: dict):
        response = await openai.ChatCompletion.acreate(
                model="gpt-4-1106-preview",
                messages=messages,
                max_tokens=300,
                temperature=0.8,
                top_p=1,
                frequency_penalty=1,
                presence_penalty=1,
                stream=True
            )
        return response

    def trigger(self, transcript: str, intent: dict = None) -> bool:
        if not intent == None:    
            question = transcript.replace(intent['GPTVerb'], '')
            messages = []
            messages.append({"role": "user", "content": question})
            asyncio.run(self._main(messages))
            return True
        return False
