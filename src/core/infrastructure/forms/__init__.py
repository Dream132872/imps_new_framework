from .auth import *
from django import forms
from shared.infrastructure import forms


class TestWidgetsForm(forms.Form):
    form_attrs = {"key": "value"}

    text_input = forms.CharField(
        widget=forms.TextInput(
            css_class="new-class-of-widget",
            help_text="This is help_text",
        ),
        placeholder="Placeholder text",
        css_class="new-class-of-form-widget",
        label="Label",
        required=False,
    )
