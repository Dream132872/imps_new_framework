from django import forms

from shared.infrastructure import forms

from .auth import *


class TestWidgetsForm(forms.Form):
    char_field = forms.CharField(required=False)
    email_field = forms.EmailField(required=False)
    url_field = forms.URLField(required=False)
    integer_input = forms.IntegerField(required=False)
