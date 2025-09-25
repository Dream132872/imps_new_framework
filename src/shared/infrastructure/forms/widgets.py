"""
Custom implemention for form widgets.
"""

from typing import Any

from django import forms
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import SafeText, mark_safe

__all__ = (
    "TextInput",
    "NumberInput",
    "EmailInput",
    "URLInput",
    "ColorInput",
    "SearchInput",
    "TelInput",
    "PasswordInput",
    "HiddenInput",
    "MultipleHiddenInput",
    "FileInput",
    "ClearableFileInput",
    "Textarea",
    "DateInput",
    "DateTimeInput",
    "TimeInput",
    "CheckboxInput",
    "Select",
    "NullBooleanSelect",
    "SelectMultiple",
    "RadioSelect",
    "CheckboxSelectMultiple",
    "MultiWidget",
    "SplitDateTimeWidget",
    "SplitHiddenDateTimeWidget",
    "SelectDateWidget",
)


class BaseCustomWidget(forms.Widget):
    """
    Base class for all custom widgets with template support and custom functionality.
    """

    template_name = None
    css_class = ""
    placeholder = ""
    help_text = ""
    required = False
    disabled = False
    readonly = False

    def __init__(self, attrs: Any = None, **kwargs) -> None:  # type: ignore
        # Extract custom attributes
        self.help_text = kwargs.pop("help_text", self.help_text)
        self.placeholder = kwargs.pop("placeholder", self.placeholder)
        self.css_class = kwargs.pop("css_class", self.css_class)
        self.required = kwargs.pop("required", self.required)
        self.disabled = kwargs.pop("disabled", self.disabled)
        self.readonly = kwargs.pop("readonly", self.readonly)

        # Initialize parent
        super().__init__(attrs)

        # Set up default attributes
        if attrs is None:
            attrs = {}

        # Add CSS class
        if self.css_class:
            current_class = attrs.get("class", "")
            attrs["class"] = f"{current_class} {self.css_class}".strip()

        # Add placeholder
        if self.placeholder:
            attrs["placeholder"] = self.placeholder

        # Add readonly/disabled attributes
        if self.readonly:
            attrs["readonly"] = True
        if self.disabled:
            attrs["disabled"] = True
        if self.required:
            attrs["required"] = True

        self.attrs.update(attrs)

    def get_context(self, name: str, value: Any, attrs: Any):
        """Get context for template rendering."""
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "help_text": self.help_text,
                "widget_obj": self,
                "flat_attrs": self.generate_flat_attributes(context["widget"]["attrs"]),
            }
        )
        import pprint
        pprint.pprint(context)
        return context

    def generate_flat_attributes(self, attrs: dict) -> str:
        flat_attrs = flatatt(
            attrs={
                key: value
                for key, value in attrs.items()
                # if key not in ["required", "disabled", "readonly"]
            }
        )

        # if self.readonly:
        #     flat_attrs += "readonly "

        # if self.disabled:
        #     flat_attrs += "disabled "

        # if self.required:
        #     flat_attrs += "required "

        return flat_attrs

    def render(
        self, name: str, value: Any, attrs: dict | None = None, renderer: Any = None
    ) -> SafeText:
        """Render widget using custom template."""
        if self.template_name:
            context = self.get_context(name, value, attrs or {})
            return mark_safe(render_to_string(self.template_name, context))
        return super().render(name, value, attrs, renderer)


class TextInput(BaseCustomWidget, forms.TextInput):
    template_name = "shared/forms/widgets/text_input.html"
    css_class = "form-control"


class NumberInput(BaseCustomWidget, forms.NumberInput):
    template_name = "shared/forms/widgets/number_input.html"
    css_class = "form-control"


class EmailInput(BaseCustomWidget, forms.EmailInput):
    template_name = "shared/forms/widgets/email_input.html"
    css_class = "form-control"


class URLInput(BaseCustomWidget, forms.URLInput):
    template_name = "shared/forms/widgets/url_input.html"
    css_class = "form-control"


class ColorInput(BaseCustomWidget, forms.ColorInput):
    template_name = "shared/forms/widgets/color_input.html"
    css_class = "form-control"


class SearchInput(BaseCustomWidget, forms.SearchInput):
    template_name = "shared/forms/widgets/search_input.html"
    css_class = "form-control"


class TelInput(BaseCustomWidget, forms.TelInput):
    template_name = "shared/forms/widgets/tel_input.html"
    css_class = "form-control"


class PasswordInput(BaseCustomWidget, forms.PasswordInput):
    template_name = "shared/forms/widgets/password_input.html"
    css_class = "form-control"


class HiddenInput(BaseCustomWidget, forms.HiddenInput):
    template_name = "shared/forms/widgets/hidden_input.html"


class MultipleHiddenInput(BaseCustomWidget, forms.MultipleHiddenInput):
    template_name = "shared/forms/widgets/multiple_hidden_input.html"


class FileInput(BaseCustomWidget, forms.FileInput):
    template_name = "shared/forms/widgets/file_input.html"
    css_class = "form-control"


class ClearableFileInput(BaseCustomWidget, forms.ClearableFileInput):
    template_name = "shared/forms/widgets/clearable_file_input.html"
    css_class = "form-control"


class Textarea(BaseCustomWidget, forms.Textarea):
    template_name = "shared/forms/widgets/textarea.html"
    css_class = "form-control"


class DateInput(BaseCustomWidget, forms.DateInput):
    template_name = "shared/forms/widgets/date_input.html"
    css_class = "form-control"


class DateTimeInput(BaseCustomWidget, forms.DateTimeInput):
    template_name = "shared/forms/widgets/datetime_input.html"
    css_class = "form-control"


class TimeInput(BaseCustomWidget, forms.TimeInput):
    template_name = "shared/forms/widgets/time_input.html"
    css_class = "form-control"


class CheckboxInput(BaseCustomWidget, forms.CheckboxInput):
    template_name = "shared/forms/widgets/checkbox_input.html"
    css_class = "form-check-input"


class Select(BaseCustomWidget, forms.Select):
    template_name = "shared/forms/widgets/select.html"
    css_class = "form-select"


class NullBooleanSelect(BaseCustomWidget, forms.NullBooleanSelect):
    template_name = "shared/forms/widgets/null_boolean_select.html"
    css_class = "form-select"


class SelectMultiple(BaseCustomWidget, forms.SelectMultiple):
    template_name = "shared/forms/widgets/select_multiple.html"
    css_class = "form-select"


class RadioSelect(BaseCustomWidget, forms.RadioSelect):
    template_name = "shared/forms/widgets/radio_select.html"
    css_class = "form-check-input"


class CheckboxSelectMultiple(BaseCustomWidget, forms.CheckboxSelectMultiple):
    template_name = "shared/forms/widgets/checkbox_select_multiple.html"
    css_class = "form-check-input"


class MultiWidget(BaseCustomWidget, forms.MultiWidget):
    template_name = "shared/forms/widgets/multi_widget.html"


class SplitDateTimeWidget(BaseCustomWidget, forms.SplitDateTimeWidget):
    template_name = "shared/forms/widgets/split_datetime_widget.html"


class SplitHiddenDateTimeWidget(BaseCustomWidget, forms.SplitHiddenDateTimeWidget):
    template_name = "shared/forms/widgets/split_hidden_datetime_widget.html"


class SelectDateWidget(BaseCustomWidget, forms.SelectDateWidget):
    template_name = "shared/forms/widgets/select_date_widget.html"
