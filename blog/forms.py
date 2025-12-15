from django import forms
from .models import Blog, Word


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'pin']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['word', 'meaning', 'example']