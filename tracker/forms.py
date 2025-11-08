from django import forms
from .models import Task, Update

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'status', 'task_type', 'target_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
