"""
Core auth forms.
"""

from core.infrastructure import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

__all__ = ("LoginForm",)

User = get_user_model()


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label=_("Username or email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "is_active", "is_superuser"]
