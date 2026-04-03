from django import forms
from .models import Blog, Word


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'pin', 'public', 'personal']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control w-100'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control w-100',
                'rows': 15
            }),
            'pin': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'personal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['word', 'meaning', 'is_phase', 'example']
        widgets = {
            'word': forms.TextInput(attrs={
                'class': 'form-control w-100'
            }),
            'meaning': forms.Textarea(attrs={
                'class': 'form-control w-100',
                'rows': 5
            }),
            'is_phase': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'example': forms.Textarea(attrs={
                'class': 'form-control w-100',
                'rows': 5
            }),
        }