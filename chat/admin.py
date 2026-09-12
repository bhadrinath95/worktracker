from django.contrib import admin
from .models import (
    Conversation,
    Message,
    LunaPrompt,
    LunaImagePrompt,
)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_at",
        "updated_at",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "role",
        "created_at",
    )

from django.contrib import admin
from .models import LunaPrompt


@admin.register(LunaPrompt)
class LunaPromptAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "title",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_display_links = (
        "title",
    )

    ordering = ("order",)

@admin.register(LunaImagePrompt)
class LunaImagePromptAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "prompt",
        "image_google_id",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "prompt",
        "image_google_id",
        "is_active",
    )

    list_display_links = (
        "id",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "prompt",
        "image_google_id",
    )

    ordering = (
        "id",
    )