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
        # LOAD ALL GROQ API KEYS
        # =========================================================

        self.api_keys = []

        for number in range(
            1,
            MAX_GROQ_KEYS + 1
        ):

            setting_name = (
                f"GROQ_API_KEY_{number}"
            )

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

        sections = (
            LunaPrompt.objects
            .filter(is_active=True)
            .order_by("order")
        )

        system_prompt = "\n\n".join(
            f"## {section.title}\n\n"
            f"{section.content}"
            for section in sections
        )

        try:

            system_prompt = system_prompt.format(
                AI_NAME=AI_NAME,
                USER_NAME=user_name
            )

        except (KeyError, ValueError):

            # If the database prompt contains braces
            # that are not formatting variables, don't
            # allow the entire request to fail.
            pass

        return system_prompt

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
    # BUILD EMERGENCY MESSAGES
    # =============================================================

    def build_emergency_messages(
        self,
        messages
    ):

        """
        Extremely small fallback request.

        This is useful when the complete Luna system
        prompt itself is too large for Groq's TPM limit.
        """

        user_message = None

        # Find the latest user message.
        for message in reversed(messages):

            role = message.get(
                "role",
                "user"
            )

            if role == "user":

                user_message = {
                    "role": "user",
                    "content": str(
                        message.get(
                            "content",
                            ""
                        )
                    )
                }

                break

        if user_message is None:

            user_message = {
                "role": "user",
                "content": "Hello"
            }

        emergency_system_prompt = (
            f"You are {AI_NAME}, "
            "a helpful AI assistant. "
            "Answer the user's message clearly "
            "and concisely."
        )

        return [
            {
                "role": "system",
                "content": emergency_system_prompt
            },
            user_message
        ]

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

            image_catalog = (
                self.get_image_catalog()
            )

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
            # BUILD NORMAL MESSAGES
            # =====================================================

            groq_messages = (
                self.build_groq_messages(
                    messages=messages,
                    system_prompt=system_prompt
                )
            )

            # =====================================================
            # LIMIT HISTORY
            # =====================================================

            groq_messages = (
                self.limit_history(
                    groq_messages,
                    MAX_HISTORY_MESSAGES
                )
            )

            print(
                f"Groq message count: "
                f"{len(groq_messages)}"
            )

            # =====================================================
            # BUILD REDUCED REQUEST
            # =====================================================

            reduced_messages = (
                self.limit_history(
                    groq_messages,
                    6
                )
            )

            # =====================================================
            # BUILD MINIMAL REQUEST
            # =====================================================

            system_message = (
                groq_messages[0]
            )

            user_messages = [
                message
                for message in groq_messages[1:]
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

            # =====================================================
            # BUILD EMERGENCY REQUEST
            # =====================================================

            emergency_messages = (
                self.build_emergency_messages(
                    messages
                )
            )

            # =====================================================
            # TRY EVERY CONFIGURED GROQ KEY
            # =====================================================

            response = None
            last_error = None

            total_keys = len(
                self.clients
            )

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

            # =====================================================
            # LOOP THROUGH ALL 15 KEYS
            # =====================================================

            for index, client in enumerate(
                self.clients
            ):

                key_number = index + 1

                print(
                    f"Trying Groq API key "
                    f"{key_number}/{total_keys}..."
                )

                # =================================================
                # REQUEST LEVELS
                # =================================================

                request_levels = [
                    (
                        "normal",
                        groq_messages
                    ),
                    (
                        "reduced",
                        reduced_messages
                    ),
                    (
                        "minimal",
                        minimal_messages
                    ),
                    (
                        "emergency",
                        emergency_messages
                    ),
                ]

                key_succeeded = False

                # =================================================
                # TRY REQUEST LEVELS
                # =================================================

                for (
                    level_name,
                    request_messages
                ) in request_levels:

                    print(
                        f"Key {key_number}: "
                        f"trying {level_name} "
                        f"payload "
                        f"({len(request_messages)} "
                        f"messages)..."
                    )

                    try:

                        response = (
                            self.make_request(
                                client,
                                request_messages
                            )
                        )

                        # =========================================
                        # SUCCESS
                        # =========================================

                        print(
                            f"Groq API key "
                            f"{key_number} succeeded "
                            f"using {level_name} payload."
                        )

                        key_succeeded = True

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
                            f"{key_number} failed "
                            f"using {level_name} payload."
                        )

                        print(
                            "Status:",
                            status_code
                        )

                        print(
                            "Error:",
                            str(e)
                        )

                        # =========================================
                        # 413 PAYLOAD / TOKEN LIMIT
                        # =========================================

                        if status_code == 413:

                            print(
                                f"Key {key_number}: "
                                f"{level_name} payload "
                                f"is too large."
                            )

                            # Try the next smaller payload.
                            continue

                        # =========================================
                        # 429 RATE LIMIT
                        # =========================================

                        if status_code == 429:

                            print(
                                f"Key {key_number} "
                                f"is rate limited."
                            )

                            # Don't waste time retrying
                            # smaller payloads on a key that
                            # is already rate limited.
                            break

                        # =========================================
                        # 401 AUTHENTICATION
                        # =========================================

                        if status_code == 401:

                            print(
                                f"Key {key_number} "
                                f"authentication failed."
                            )

                            break

                        # =========================================
                        # 403 FORBIDDEN
                        # =========================================

                        if status_code == 403:

                            print(
                                f"Key {key_number} "
                                f"was forbidden."
                            )

                            break

                        # =========================================
                        # OTHER ERROR
                        # =========================================

                        print(
                            f"Unhandled error for "
                            f"Groq API key "
                            f"{key_number}."
                        )

                        # Move to next API key.
                        break

                # =================================================
                # CURRENT KEY FAILED
                # =================================================

                if not key_succeeded:

                    print(
                        f"Groq API key "
                        f"{key_number} failed all "
                        f"available request levels."
                    )

                    # IMPORTANT:
                    # Never return here.
                    #
                    # Continue to the next API key.
                    if key_number < total_keys:

                        print(
                            f"Switching to Groq API key "
                            f"{key_number + 1}..."
                        )

                    else:

                        print(
                            "This was the final "
                            "configured Groq API key."
                        )

                    continue

                # =================================================
                # SUCCESSFUL KEY
                # =================================================

                break

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

            response_text = (
                response_text.strip()
            )

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
            # RETURN SUCCESS
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