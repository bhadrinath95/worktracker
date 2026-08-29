import os
import json
import urllib.request
import urllib.error
from threading import Lock
from django.conf import settings
from django.contrib.auth.decorators import login_required


AI_NAME = "Luna"

# Gemini API
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Use a Gemini model available on the free tier
GEMINI_MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = f"""
Your name is {AI_NAME}.
You are a helpful AI assistant.
If the user asks for your name, tell them your name is {AI_NAME}.

When expressing emotions, gestures, reactions, or actions, use appropriate
Unicode emojis instead of writing actions between asterisks.

For example:

Use 👋 instead of waves
Use 😊 instead of smiles
Use 🤔 instead of thinks
Use 😂 instead of laughs
Use 😢 instead of cries
Use 👏 instead of claps

Do not use stage directions such as waves, smiles, laughs, etc.
Prefer natural conversational responses with emojis when appropriate.
"""


class GeminiService:

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def generate(self, messages):

        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not configured."
            )

        # Convert your existing OpenAI/Llama-style messages
        # into Gemini format.

        contents = []

        for message in messages:

            role = message.get("role", "user")
            content = message.get("content", "")

            # Ignore system messages because we send SYSTEM_PROMPT
            # separately to Gemini.
            if role == "system":
                continue

            # Gemini uses "user" and "model"
            if role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"

            contents.append({
                "role": gemini_role,
                "parts": [
                    {
                        "text": content
                    }
                ]
            })

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "system_instruction": {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT
                    }
                ]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 1024
            }
        }

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:

            with urllib.request.urlopen(request, timeout=120) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            # Extract Gemini response
            candidates = result.get("candidates", [])

            if not candidates:
                return "Sorry, I couldn't generate a response."

            parts = candidates[0].get("content", {}).get("parts", [])

            response_text = "".join(
                part.get("text", "")
                for part in parts
            )

            return response_text.strip()

        except urllib.error.HTTPError as e:

            error_body = e.read().decode("utf-8")

            print("Gemini API HTTP Error:")
            print(error_body)

            return "Sorry, Luna is currently unable to respond."

        except urllib.error.URLError as e:

            print("Gemini API connection error:")
            print(e)

            return "Sorry, Luna could not connect to the AI service."

        except Exception as e:

            print("Gemini API error:")
            print(e)

            return "Sorry, something went wrong while generating the response."


gemini_service = GeminiService()