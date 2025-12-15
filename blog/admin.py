from django.contrib import admin
from .models import Blog, Word, Tag

# Register your models here.
admin.site.register(Blog)
admin.site.register(Word)
admin.site.register(Tag)