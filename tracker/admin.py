from django.contrib import admin
from .models import Task, Update, TaskType

# Register your models here.
admin.site.register(TaskType)
admin.site.register(Task)
admin.site.register(Update)
