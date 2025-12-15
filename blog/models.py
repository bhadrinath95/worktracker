from django.db import models

# Create your models here.
from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="HTML content allowed")
    created_at = models.DateTimeField(auto_now_add=True)
    pin = models.BooleanField(default=False)


    def __str__(self):
        return self.title
    
class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    meaning = models.TextField()
    example = models.TextField(help_text="Usage example", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    syntax = models.TextField(help_text="HTML syntax with placeholders")

    def __str__(self):
        return self.name
