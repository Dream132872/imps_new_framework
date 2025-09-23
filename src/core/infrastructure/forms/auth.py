"""
Core auth forms.
"""

from django import forms
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label=_("Username or email"))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())
