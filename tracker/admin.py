from django.contrib import admin
from .models import Task, Update, TaskType, LifePrincipleTopic, LifePrinciple, Document, UpdateTemplate


class LifePrincipleTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic')


class LifePrincipleAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'principle_short', 'meaning_short')
    list_filter = ('topic',)
    search_fields = ('principle', 'meaning')

    def principle_short(self, obj):
        return (obj.principle[:50] + '...') if len(obj.principle) > 50 else obj.principle
    principle_short.short_description = "Principle"

    def meaning_short(self, obj):
        return (obj.meaning[:50] + '...') if len(obj.meaning) > 50 else obj.meaning
    meaning_short.short_description = "Meaning"
    
# Register your models here.
admin.site.register(TaskType)
admin.site.register(Task)
admin.site.register(Update)
admin.site.register(LifePrincipleTopic, LifePrincipleTopicAdmin)
admin.site.register(LifePrinciple, LifePrincipleAdmin)
admin.site.register(Document)
admin.site.register(UpdateTemplate)