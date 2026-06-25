# forms.py
from django import forms
from django.forms import modelformset_factory
from .models import Task, Update, Document, UpdateTemplate, Todo

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'status', 'task_type', 'started_date', 'target_date', 'is_important', 'is_bookmark', 'is_private', 'is_template']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'started_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_bookmark': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class TaskFromTemplateForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=Task.objects.filter(is_template=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    started_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    target_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
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
        fields = ['template', 'name', 'date', 'start_time',  'end_time', 'description', 'is_check_box', 'status', 'reminder_type', 'date_to_remind', 'can_store_reminder', 'auto_reminder_handle']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_check_box': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'date_to_remind': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Days to remind',
                'min': 1,
                'max': 31,
                'step': 1
            }),
        }

class MultipleUpdateForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=UpdateTemplate.objects.all().order_by('name'),
        required=False,
        empty_label="Select a template",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Template"
    )

    dates = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="Dates"
    )

    class Meta:
        model = Update
        fields = ['template', 'name', 'dates', 'start_time', 'end_time', 'description', 'is_check_box', 'status', 'reminder_type', 'date_to_remind', 'can_store_reminder', 'auto_reminder_handle']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_check_box': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'date_to_remind': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Days to remind',
                'min': 1,
                'max': 31,
                'step': 1
            }),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['filename', 'fileurl', 'is_web_link']
        widgets = {
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
            'fileurl': forms.TextInput(attrs={'class': 'form-control'}),
            'is_check_box': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1, can_delete=True)

class TodoForm(forms.ModelForm):

    class Meta:
        model = Todo
        fields = ['date', 'description', 'is_completed']

        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }