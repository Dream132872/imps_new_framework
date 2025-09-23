from .auth import *
from django import forms
from shared.infrastructure import forms


class TestWidgetsForm(forms.Form):
    form_attrs = {"key": "value"}

    text_input = forms.CharField(
        widget=forms.TextInput(
            required=False,
            help_text="This is help_text",
            placeholder="Placeholder text",
            label="Label",
        )
    )
