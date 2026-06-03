from django import forms
from .models import Statement, DecisionTree


class DecisionTreeForm(forms.ModelForm):

    class Meta:
        model = DecisionTree

        fields = [
            "name",
            "description"
        ]
        
class StatementForm(forms.ModelForm):

    class Meta:
        model = Statement
        fields = [
            "tree",
            "title",
            "description",
            "parent",   
            "status",
        ]