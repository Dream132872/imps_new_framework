"""
Core auth forms.
"""

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from core.infrastructure import forms

__all__ = ("LoginForm",)

User = get_user_model()


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label=_("Username or email"),
        required=True,
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(),
        required=True,
    )
