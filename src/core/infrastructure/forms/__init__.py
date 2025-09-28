from typing import Any
from django import forms
from django.forms import widgets
from shared.infrastructure import forms
from django.utils.translation import gettext_lazy as _
from .auth import *
from django.core.exceptions import ValidationError


class TestWidgetsForm(forms.Form):
    form_title = _("Test form")

    char_field = forms.CharField(required=False)
    email_field = forms.EmailField(required=False)
    url_field = forms.URLField(required=False)
    integer_input = forms.IntegerField(required=False)
    checkbox_input = forms.BooleanField()
    color_input = forms.CharField(widget=forms.ColorInput())
    search_input = forms.CharField(widget=forms.SearchInput())
    tel_input = forms.CharField(widget=forms.TelInput())
    password_input = forms.CharField(widget=forms.PasswordInput())
    hidden_input = forms.CharField(widget=forms.HiddenInput())
