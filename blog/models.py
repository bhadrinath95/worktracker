from django.db import models
from django.utils.text import slugify

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="HTML content allowed")
    created_at = models.DateTimeField(auto_now_add=True)
    pin = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)
    public = models.BooleanField(default=False) 
    personal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    is_phase = models.BooleanField(default=False)
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
