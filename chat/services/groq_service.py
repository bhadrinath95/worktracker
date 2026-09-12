import re

from threading import Lock

from django.conf import settings

from groq import Groq

from chat.models import (
    LunaPrompt,
    LunaImagePrompt,
)


AI_NAME = "Luna"
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

        # Prevent creating clients multiple times
        if hasattr(self, "clients"):
            return

        # -----------------------------------------
        # GROQ API KEYS
        # -----------------------------------------

        api_keys = [
            getattr(settings, "GROQ_API_KEY_1", ""),
            getattr(settings, "GROQ_API_KEY_2", ""),
            getattr(settings, "GROQ_API_KEY_3", ""),
            getattr(settings, "GROQ_API_KEY_4", ""),
        ]

        # Remove empty keys
        self.api_keys = [
            key for key in api_keys
            if key
        ]

        if not self.api_keys:
            raise ValueError(
                "No GROQ API keys are configured."
            )

        # -----------------------------------------
        # CREATE GROQ CLIENTS
        # -----------------------------------------

        self.clients = [
            Groq(api_key=key)
            for key in self.api_keys
        ]

    # =============================================
    # SYSTEM PROMPT
    # =============================================

    def get_system_prompt(
        self,
        user_name=""
    ):

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

    # =============================================
    # IMAGE CATALOG
    # =============================================

    def get_image_catalog(self):

        image_prompts = (
            LunaImagePrompt.objects
            .filter(is_active=True)
            .order_by("id")
        )

        if not image_prompts:
            return ""

        lines = []

        for image in image_prompts:

            lines.append(
                f"IMAGE_ID: {image.id}\n"
                f"DESCRIPTION: {image.prompt}"
            )

        return "\n\n".join(lines)

    # =============================================
    # GENERATE
    # =============================================

    def generate(
        self,
        messages,
        user_name=""
    ):

        try:

            # -----------------------------------------
            # SYSTEM PROMPT
            # -----------------------------------------

            system_prompt = self.get_system_prompt(
                user_name=user_name
            )

            # -----------------------------------------
            # IMAGE CATALOG
            # -----------------------------------------

            image_catalog = self.get_image_catalog()

            if image_catalog:

                system_prompt += f"""

## LUNA IMAGE SELECTION

You have access to predefined images of Luna.

When the user asks for a photo, picture, image,
or visual representation of Luna, choose the
most suitable image from the available images.

Only select an image when it is relevant to
the user's request.

If a suitable image exists, add this marker
at the very END of your response:

[IMAGE_ID:123]

Replace 123 with the IMAGE_ID of the selected image.

IMPORTANT:

- Only use IMAGE_ID values from the image catalog.
- Never invent an IMAGE_ID.
- Select only one image.
- Do not mention the IMAGE_ID to the user.
- If no suitable image exists, do not add an IMAGE_ID marker.

AVAILABLE IMAGES:

{image_catalog}
"""

            # -----------------------------------------
            # GROQ MESSAGES
            # -----------------------------------------

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

            # -----------------------------------------
            # FALLBACK
            # -----------------------------------------

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

            # -----------------------------------------
            # TRY ALL GROQ KEYS
            # -----------------------------------------

            response = None

            for index, client in enumerate(
                self.clients
            ):

                key_number = index + 1

                try:

                    print(
                        f"Trying Groq API key "
                        f"{key_number}..."
                    )

                    response = (
                        client.chat.completions.create(
                            model=GROQ_MODEL,
                            messages=groq_messages,
                            temperature=0.7,
                            max_completion_tokens=512,
                            reasoning_effort="low",
                        )
                    )

                    # Success
                    print(
                        f"Groq API key "
                        f"{key_number} succeeded."
                    )

                    break

                except Exception as e:

                    status_code = getattr(
                        e,
                        "status_code",
                        None
                    )

                    print(
                        f"Groq API key "
                        f"{key_number} failed."
                    )

                    print(
                        "Status:",
                        status_code
                    )

                    print(
                        "Error:",
                        str(e)
                    )

                    # ---------------------------------
                    # RATE LIMIT
                    # ---------------------------------

                    if status_code == 429:

                        print(
                            f"Key {key_number} "
                            f"has reached its rate limit."
                        )

                        # Try next key
                        continue

                    # ---------------------------------
                    # AUTHENTICATION ERROR
                    # ---------------------------------

                    if status_code == 401:

                        print(
                            f"Key {key_number} "
                            f"authentication failed."
                        )

                        # Try next key too
                        continue

                    # ---------------------------------
                    # FORBIDDEN
                    # ---------------------------------

                    if status_code == 403:

                        print(
                            f"Key {key_number} "
                            f"was forbidden."
                        )

                        # Try next key
                        continue

                    # ---------------------------------
                    # OTHER ERROR
                    # ---------------------------------

                    raise

            # -----------------------------------------
            # ALL KEYS FAILED
            # -----------------------------------------

            if response is None:

                return {
                    "text": (
                        "Sorry, Luna is temporarily "
                        "unable to respond because "
                        "all available Groq API keys "
                        "have reached their limits."
                    ),
                    "image_id": None,
                }

            # -----------------------------------------
            # EMPTY RESPONSE
            # -----------------------------------------

            if not response.choices:

                return {
                    "text": (
                        "Sorry, I couldn't "
                        "generate a response."
                    ),
                    "image_id": None,
                }

            response_text = (
                response
                .choices[0]
                .message
                .content
            )

            if not response_text:

                return {
                    "text": (
                        "Sorry, I couldn't "
                        "generate a response."
                    ),
                    "image_id": None,
                }

            response_text = response_text.strip()

            # -----------------------------------------
            # EXTRACT IMAGE ID
            # -----------------------------------------

            image_id = None

            match = re.search(
                r"\[IMAGE_ID:(\d+)\]",
                response_text
            )

            if match:

                image_id = int(
                    match.group(1)
                )

                response_text = re.sub(
                    r"\s*\[IMAGE_ID:\d+\]\s*",
                    "",
                    response_text
                ).strip()

            # -----------------------------------------
            # RETURN
            # -----------------------------------------

            return {
                "text": response_text,
                "image_id": image_id,
            }

        # =============================================
        # GENERAL ERROR
        # =============================================

        except Exception as e:

            print(
                "===================================="
            )

            print(
                "Groq API Error"
            )

            print(
                type(e).__name__
            )

            print(
                str(e)
            )

            print(
                "===================================="
            )

            return {
                "text": (
                    "Sorry, something went wrong "
                    "while generating the response."
                ),
                "image_id": None,
            }


groq_service = GroqService()