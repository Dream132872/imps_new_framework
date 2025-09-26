from .auth import *
from django import forms
from shared.infrastructure import forms


class TestWidgetsForm(forms.Form):
    text_input = forms.CharField(
        help_text="This is help_text",
        placeholder="Placeholder text",
        css_class="new-class-of-form-widget",
        required=False,
        label="Label",
    )
