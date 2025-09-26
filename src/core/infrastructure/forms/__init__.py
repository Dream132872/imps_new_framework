from django import forms

from shared.infrastructure import forms

from .auth import *


class TestWidgetsForm(forms.Form):
    char_field = forms.CharField()

    email_field = forms.EmailField()

    url_field = forms.URLField()
