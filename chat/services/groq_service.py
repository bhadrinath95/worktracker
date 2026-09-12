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

# Maximum number of conversation messages sent to Groq.
# System prompt is kept separately.
MAX_HISTORY_MESSAGES = 15

# Maximum number of API keys supported.
MAX_GROQ_KEYS = 15


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

        # Prevent creating clients multiple times.
        if hasattr(self, "clients"):
            return

        # =========================================================
        # LOAD ALL 15 GROQ API KEYS
        # =========================================================

        self.api_keys = []

        for number in range(1, MAX_GROQ_KEYS + 1):

            setting_name = f"GROQ_API_KEY_{number}"

            key = getattr(
                settings,
                setting_name,
                ""
            )

            if key:
                key = str(key).strip()

            if key:
                self.api_keys.append(key)

        # =========================================================
        # VALIDATE KEYS
        # =========================================================

        if not self.api_keys:
            raise ValueError(
                "No GROQ API keys are configured."
            )

        # =========================================================
        # CREATE CLIENTS
        # =========================================================

        self.clients = [
            Groq(api_key=key)
            for key in self.api_keys
        ]

        print(
            "===================================="
        )
        print(
            f"Groq API keys configured: "
            f"{len(self.clients)}/{MAX_GROQ_KEYS}"
        )
        print(
            "===================================="
        )

    # =============================================================
    # SYSTEM PROMPT
    # =============================================================

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

    # =============================================================
    # IMAGE CATALOG
    # =============================================================

    def get_image_catalog(self):

        image_prompts = (
            LunaImagePrompt.objects
            .filter(is_active=True)
            .order_by("id")
        )

        if not image_prompts.exists():
            return ""

        lines = []

        for image in image_prompts:

            lines.append(
                f"IMAGE_ID: {image.id}\n"
                f"DESCRIPTION: {image.prompt}"
            )

        return "\n\n".join(lines)

    # =============================================================
    # BUILD GROQ MESSAGES
    # =============================================================

    def build_groq_messages(
        self,
        messages,
        system_prompt
    ):

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

            # Never allow another system message.
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

        # =========================================================
        # FALLBACK USER MESSAGE
        # =========================================================

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

        return groq_messages

    # =============================================================
    # LIMIT CONVERSATION HISTORY
    # =============================================================

    def limit_history(
        self,
        groq_messages,
        max_messages=MAX_HISTORY_MESSAGES
    ):

        # +1 because system prompt is separate.
        if len(groq_messages) <= max_messages + 1:
            return groq_messages

        system_message = groq_messages[0]

        recent_messages = groq_messages[
            -max_messages:
        ]

        return [
            system_message
        ] + recent_messages

    # =============================================================
    # GROQ REQUEST
    # =============================================================

    def make_request(
        self,
        client,
        groq_messages
    ):

        return client.chat.completions.create(
            model=GROQ_MODEL,
            messages=groq_messages,
            temperature=0.7,
            max_completion_tokens=512,
            reasoning_effort="low",
        )

    # =============================================================
    # GENERATE
    # =============================================================

    def generate(
        self,
        messages,
        user_name=""
    ):

        try:

            # =====================================================
            # SYSTEM PROMPT
            # =====================================================

            system_prompt = self.get_system_prompt(
                user_name=user_name
            )

            # =====================================================
            # IMAGE CATALOG
            # =====================================================

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

            # =====================================================
            # BUILD MESSAGES
            # =====================================================

            groq_messages = self.build_groq_messages(
                messages=messages,
                system_prompt=system_prompt
            )

            # =====================================================
            # LIMIT HISTORY
            # =====================================================

            groq_messages = self.limit_history(
                groq_messages,
                MAX_HISTORY_MESSAGES
            )

            print(
                f"Groq message count: "
                f"{len(groq_messages)}"
            )

            # =====================================================
            # TRY EVERY CONFIGURED GROQ KEY
            # =====================================================

            response = None
            last_error = None

            total_keys = len(self.clients)

            print(
                "===================================="
            )
            print(
                f"Starting Groq request with "
                f"{total_keys} configured API keys."
            )
            print(
                "===================================="
            )

            for index, client in enumerate(
                self.clients
            ):

                key_number = index + 1

                print(
                    f"Trying Groq API key "
                    f"{key_number}/{total_keys}..."
                )

                try:

                    response = self.make_request(
                        client,
                        groq_messages
                    )

                    # =================================================
                    # SUCCESS
                    # =================================================

                    print(
                        f"Groq API key "
                        f"{key_number} succeeded."
                    )

                    break

                except Exception as e:

                    last_error = e

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

                    # =================================================
                    # 429 RATE LIMIT
                    # =================================================

                    if status_code == 429:

                        print(
                            f"Key {key_number} "
                            f"is rate limited."
                        )

                        if key_number < total_keys:

                            print(
                                f"Immediately switching "
                                f"to Groq API key "
                                f"{key_number + 1}..."
                            )

                        else:

                            print(
                                "All configured Groq "
                                "API keys are rate limited."
                            )

                        # IMPORTANT:
                        # Do NOT return here.
                        # Continue to the next key.
                        continue

                    # =================================================
                    # 401 AUTHENTICATION ERROR
                    # =================================================

                    if status_code == 401:

                        print(
                            f"Key {key_number} "
                            f"authentication failed."
                        )

                        print(
                            "Trying next API key..."
                        )

                        continue

                    # =================================================
                    # 403 FORBIDDEN
                    # =================================================

                    if status_code == 403:

                        print(
                            f"Key {key_number} "
                            f"was forbidden."
                        )

                        print(
                            "Trying next API key..."
                        )

                        continue

                    # =================================================
                    # 413 PAYLOAD TOO LARGE
                    # =================================================

                    if status_code == 413:

                        print(
                            "Payload too large."
                        )

                        # ---------------------------------------------
                        # REDUCE HISTORY
                        # ---------------------------------------------

                        reduced_messages = (
                            self.limit_history(
                                groq_messages,
                                6
                            )
                        )

                        print(
                            f"Retrying key "
                            f"{key_number} with "
                            f"{len(reduced_messages)} "
                            f"messages..."
                        )

                        try:

                            response = self.make_request(
                                client,
                                reduced_messages
                            )

                            print(
                                f"Groq API key "
                                f"{key_number} succeeded "
                                f"after reducing "
                                f"conversation history."
                            )

                            break

                        except Exception as retry_error:

                            retry_status = getattr(
                                retry_error,
                                "status_code",
                                None
                            )

                            last_error = retry_error

                            print(
                                "Reduced payload "
                                "retry failed."
                            )

                            print(
                                "Status:",
                                retry_status
                            )

                            print(
                                "Error:",
                                str(retry_error)
                            )

                            # -----------------------------------------
                            # REDUCED REQUEST = 429
                            # -----------------------------------------

                            if retry_status == 429:

                                print(
                                    f"Key {key_number} "
                                    f"is rate limited "
                                    f"after payload retry."
                                )

                                print(
                                    "Trying next API key..."
                                )

                                continue

                            # -----------------------------------------
                            # STILL 413
                            # -----------------------------------------

                            if retry_status == 413:

                                system_message = (
                                    reduced_messages[0]
                                )

                                user_messages = [
                                    message
                                    for message
                                    in reduced_messages[1:]
                                    if message["role"] == "user"
                                ]

                                if user_messages:

                                    minimal_messages = [
                                        system_message,
                                        user_messages[-1]
                                    ]

                                else:

                                    minimal_messages = [
                                        system_message,
                                        {
                                            "role": "user",
                                            "content": "Hello"
                                        }
                                    ]

                                print(
                                    "Retrying with minimal "
                                    "conversation payload..."
                                )

                                try:

                                    response = self.make_request(
                                        client,
                                        minimal_messages
                                    )

                                    print(
                                        f"Groq API key "
                                        f"{key_number} succeeded "
                                        f"with minimal payload."
                                    )

                                    break

                                except Exception as final_error:

                                    final_status = getattr(
                                        final_error,
                                        "status_code",
                                        None
                                    )

                                    last_error = final_error

                                    print(
                                        "Minimal payload "
                                        "retry failed."
                                    )

                                    print(
                                        "Status:",
                                        final_status
                                    )

                                    print(
                                        "Error:",
                                        str(final_error)
                                    )

                                    # ---------------------------------
                                    # MINIMAL RETRY = 429
                                    # ---------------------------------

                                    if final_status == 429:

                                        print(
                                            f"Key {key_number} "
                                            f"is rate limited "
                                            f"during minimal retry."
                                        )

                                        print(
                                            "Trying next API key..."
                                        )

                                        continue

                                    # ---------------------------------
                                    # STILL 413
                                    # ---------------------------------

                                    if final_status == 413:

                                        return {
                                            "text": (
                                                "Sorry, the "
                                                "conversation is "
                                                "too large to process. "
                                                "Please start a new "
                                                "conversation."
                                            ),
                                            "image_id": None,
                                        }

                                    # ---------------------------------
                                    # OTHER FINAL ERROR
                                    # ---------------------------------

                                    continue

                            # -----------------------------------------
                            # OTHER RETRY ERROR
                            # -----------------------------------------

                            continue

                    # =================================================
                    # OTHER ERROR
                    # =================================================

                    print(
                        f"Unhandled error for "
                        f"Groq API key {key_number}."
                    )

                    print(
                        "Trying next API key..."
                    )

                    continue

            # =========================================================
            # ALL KEYS FAILED
            # =========================================================

            if response is None:

                print(
                    "===================================="
                )

                print(
                    "ALL CONFIGURED GROQ API KEYS FAILED."
                )

                print(
                    f"Total keys attempted: "
                    f"{total_keys}"
                )

                if last_error:

                    print(
                        "Last error:",
                        str(last_error)
                    )

                print(
                    "===================================="
                )

                return {
                    "text": (
                        "Sorry, Luna is temporarily "
                        "unable to respond because "
                        "all available Groq API keys "
                        "have reached their limits."
                    ),
                    "image_id": None,
                }

            # =========================================================
            # EMPTY RESPONSE
            # =========================================================

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

            # =========================================================
            # EXTRACT IMAGE ID
            # =========================================================

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

            # =========================================================
            # RETURN
            # =========================================================

            return {
                "text": response_text,
                "image_id": image_id,
            }

        # =============================================================
        # GENERAL ERROR
        # =============================================================

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


# =============================================================
# SINGLETON INSTANCE
# =============================================================

groq_service = GroqService()