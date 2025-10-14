"""
core auth forms.
"""

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from parsley.decorators import parsleyfy

from core.infrastructure import forms

__all__ = ("LoginForm",)

User = get_user_model()


@parsleyfy
class LoginForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        required=True,
        placeholder=_("Username"),
        widget=forms.TextInput(
            attrs={
                "data-parsley-errors-container": "#username_errors",
            }
        ),
    )

    password = forms.CharField(
        label=_("Password"),
        required=True,
        placeholder=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "data-parsley-errors-container": "#password_errors",
            }
        ),
    )
