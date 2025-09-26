from django import forms

from shared.infrastructure import forms

from .auth import *


class TestWidgetsForm(forms.Form):
    text_input = forms.CharField(
        help_text="This is help_text",
        placeholder="Placeholder text",
        required=True,
        label="Label",
    )
