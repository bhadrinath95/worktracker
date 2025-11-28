# forms.py
from django import forms
from django.forms import modelformset_factory
from .models import Task, Update, Document, UpdateTemplate

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'status', 'task_type', 'started_date', 'target_date', 'is_hold', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'started_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class UpdateForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=UpdateTemplate.objects.all().order_by('name'),
        required=False,
        empty_label="Select a template",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Template"
    )

    class Meta:
        model = Update
        fields = ['template', 'date', 'description', 'is_check_box', 'is_completed']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_check_box': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['filename', 'fileurl']
        widgets = {
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
            'fileurl': forms.TextInput(attrs={'class': 'form-control'}),
        }

DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1, can_delete=True)
