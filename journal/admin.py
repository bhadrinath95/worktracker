from django.contrib import admin
from .models import Topic, Story


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ["heading", "topic", "story_datetime"]
    list_filter = ["topic", "story_datetime"]
    search_fields = ["heading", "description"]
    date_hierarchy = "story_datetime"
