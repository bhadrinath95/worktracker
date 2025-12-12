from django import forms
from django.forms import inlineformset_factory
from .models import Statement, StatementOption


class StatementForm(forms.ModelForm):
    class Meta:
        model = Statement
        fields = [
            "title",
            "statement_text",
            "conclusion",
            "status",
        ]


class StatementOptionForm(forms.ModelForm):
    class Meta:
        model = StatementOption
        fields = [
            "option_description",
            "decision",
            "cancelled_principles",
            "advice_from",
            "advice_reason",
        ]
        widgets = {
            "cancelled_principles": forms.SelectMultiple(attrs={
                "class": "select2-multi"
            })
        }


StatementOptionFormSet = inlineformset_factory(
    Statement,
    StatementOption,
    form=StatementOptionForm,
    extra=1,
    can_delete=True
)
