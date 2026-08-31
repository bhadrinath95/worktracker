import json
from threading import Lock

from anyio import Path
from django.conf import settings
from groq import Groq
from pathlib import Path
from chat.models import LunaPrompt


AI_NAME = "Luna"

GROQ_API_KEY = settings.GROQ_API_KEY

GROQ_MODEL = settings.GROQ_MODEL


class GroqService:

    _instance = None
    _lock = Lock()

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance


    def __init__(self):

        # Prevent creating the client multiple times
        if hasattr(self, "client"):
            return

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=GROQ_API_KEY
        )


    def get_system_prompt(self, user_name=""):

        sections = LunaPrompt.objects.filter(
            is_active=True
        ).order_by("order")

        system_prompt = "\n\n".join(
            f"## {section.title}\n\n{section.content}"
            for section in sections
        )

        return system_prompt.format(
            AI_NAME=AI_NAME,
            USER_NAME=user_name
        )
    
    def generate(self, messages, user_name=""):
    
        try:

            system_prompt = self.get_system_prompt(
                user_name=user_name
            )

            groq_messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            for message in messages:

                role = message.get(
                    "role",
                    "user"
                )

                content = str(
                    message.get(
                        "content",
                        ""
                    )
                )

                if role == "system":
                    continue

                if role == "assistant":
                    groq_role = "assistant"
                else:
                    groq_role = "user"

                groq_messages.append(
                    {
                        "role": groq_role,
                        "content": content
                    }
                )

            if not any(
                message["role"] == "user"
                for message in groq_messages
            ):
                groq_messages.append(
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                )

            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=groq_messages,
                    temperature=0.7,
                    max_completion_tokens=512,
                    reasoning_effort="low",
                )

            except Exception as e:
                print("GROQ ERROR:", repr(e))
                raise

            if not response.choices:
                return "Sorry, I couldn't generate a response."

            response_text = response.choices[0].message.content

            if not response_text:
                return "Sorry, I couldn't generate a response."

            return response_text.strip()

        except Exception as e:

            print("====================================")
            print("Groq API Error")
            print(type(e).__name__)
            print(str(e))
            print("====================================")

            if getattr(e, "status_code", None) == 429:
                return (
                    "Sorry, Luna has temporarily "
                    "reached the Groq API rate limit. "
                    "Please try again later."
                )

            if getattr(e, "status_code", None) == 401:
                return (
                    "Sorry, Luna's Groq API "
                    "authentication failed."
                )

            if getattr(e, "status_code", None) == 403:
                return (
                    "Sorry, Luna's Groq request "
                    "was forbidden by the API."
                )

            return (
                "Sorry, something went wrong while "
                "generating the response."
            )


groq_service = GroqService()