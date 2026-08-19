from django import forms
from .models import Music, Artist, Category


class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = [
            "title",
            "artists",
            "category",
            "fileurl",
            "description",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter song title",
            }),
            "artists": forms.SelectMultiple(
                attrs={
                    "class": "form-select music-artists",
                    "multiple": "multiple",
                }
            ),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "fileurl": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter GitHub file name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter description",
            }),
        }


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter artist name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter artist description",
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter category description",
            }),
        }