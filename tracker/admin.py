from django.contrib import admin
from .models import Task, Update, TaskType, LifePrinciple

# Register your models here.
admin.site.register(TaskType)
admin.site.register(Task)
admin.site.register(Update)
admin.site.register(LifePrinciple)
