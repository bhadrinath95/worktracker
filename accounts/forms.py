from django import forms
from .models import UserProfile

class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = "__all__"
        widgets = {
            'special_privilege_password': forms.PasswordInput(render_value=True),
        }