"""
Custom implementation for form widgets.
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
    default_css_class = ""
    help_text = ""
    field: Any = None

    def __init__(
        self,
        attrs: dict | None = None,
        help_text: str = "",
        placeholder: str = "",
        css_class: str = "",
        required: bool = False,
        disabled: bool = False,
        readonly: bool = False,
    ) -> None:
        # Initialize parent
        super().__init__(attrs)

        # Extract custom attributes
        self.help_text = help_text
        self.placeholder = placeholder

        if required:
            self.required = required

        if disabled:
            self.disabled = disabled

        if readonly:
            self.readonly = readonly

        # Set up default attributes
        if attrs is None:
            attrs = {}

        # Add default CSS class of the widget
        if self.default_css_class:
            self.add_css_classes(self.default_css_class)

        # Add CSS class
        if css_class:
            self.add_css_classes(css_class)

        self.attrs.update(attrs)

    def get_context(self, name: str, value: Any, attrs: Any):
        """Get context for template rendering."""
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "help_text": self.help_text,
                "widget_obj": self,
                "flat_attrs": self.generate_flatten_attrs(context["widget"]["attrs"]),
                "field": self.field,
            }
        )

        return context

    def generate_flatten_attrs(self, attrs: dict) -> str:
        """Generated flatten attributes for widget.

        Args:
            attrs (dict): all attributes of this widget.

        Returns:
            str: flatten attributes.
        """
        flat_attrs = flatatt(attrs={key: value for key, value in attrs.items()})

        return flat_attrs

    def add_css_classes(self, css_classes: str) -> None:
        """Adds new classes to the input.

        Args:
            css_classes (str): css class names
        """

        current_classes = self.attrs.get("class", "")
        self.attrs["class"] = f"{current_classes} {css_classes}".strip()

    @property
    def css_class(self) -> str:
        return self.attrs.get("class", "")

    @css_class.setter
    def css_class(self, value: str) -> None:
        self.add_css_classes(value)

    @property
    def placeholder(self) -> str:
        return self.attrs.get("placeholder", "")

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self.attrs["placeholder"] = value

    @property
    def disabled(self) -> bool:
        return self.attrs.get("disabled", False)

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.attrs["disabled"] = True
        else:
            try:
                self.attrs.pop("disabled")
            except:
                pass

    @property
    def readonly(self) -> bool:
        return self.attrs.get("readonly", False)

    @readonly.setter
    def readonly(self, value: bool) -> None:
        if value:
            self.attrs["readonly"] = True
        else:
            try:
                self.attrs.pop("readonly")
            except:
                pass

    @property
    def required(self) -> bool:
        return self.attrs.get("required", False)

    @required.setter
    def required(self, value: bool) -> None:
        if value:
            self.attrs["required"] = True
        else:
            try:
                self.attrs.pop("required")
            except:
                pass

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
    default_css_class = "form-control"


class NumberInput(BaseCustomWidget, forms.NumberInput):
    template_name = "shared/forms/widgets/number_input.html"
    default_css_class = "form-control"


class EmailInput(BaseCustomWidget, forms.EmailInput):
    template_name = "shared/forms/widgets/email_input.html"
    default_css_class = "form-control"


class URLInput(BaseCustomWidget, forms.URLInput):
    template_name = "shared/forms/widgets/url_input.html"
    default_css_class = "form-control"


class ColorInput(BaseCustomWidget, forms.ColorInput):
    template_name = "shared/forms/widgets/color_input.html"
    default_css_class = "form-control"


class SearchInput(BaseCustomWidget, forms.SearchInput):
    template_name = "shared/forms/widgets/search_input.html"
    default_css_class = "form-control"


class TelInput(BaseCustomWidget, forms.TelInput):
    template_name = "shared/forms/widgets/tel_input.html"
    default_css_class = "form-control"


class PasswordInput(BaseCustomWidget, forms.PasswordInput):
    template_name = "shared/forms/widgets/password_input.html"
    default_css_class = "form-control"


class HiddenInput(BaseCustomWidget, forms.HiddenInput):
    template_name = "shared/forms/widgets/hidden_input.html"


class MultipleHiddenInput(BaseCustomWidget, forms.MultipleHiddenInput):
    template_name = "shared/forms/widgets/multiple_hidden_input.html"


class FileInput(BaseCustomWidget, forms.FileInput):
    template_name = "shared/forms/widgets/file_input.html"
    default_css_class = "form-control"


class ClearableFileInput(BaseCustomWidget, forms.ClearableFileInput):
    template_name = "shared/forms/widgets/clearable_file_input.html"
    default_css_class = "form-control"


class Textarea(BaseCustomWidget, forms.Textarea):
    template_name = "shared/forms/widgets/textarea.html"
    default_css_class = "form-control"


class DateInput(BaseCustomWidget, forms.DateInput):
    template_name = "shared/forms/widgets/date_input.html"
    default_css_class = "form-control"


class DateTimeInput(BaseCustomWidget, forms.DateTimeInput):
    template_name = "shared/forms/widgets/datetime_input.html"
    default_css_class = "form-control"


class TimeInput(BaseCustomWidget, forms.TimeInput):
    template_name = "shared/forms/widgets/time_input.html"
    default_css_class = "form-control"


class CheckboxInput(BaseCustomWidget, forms.CheckboxInput):
    template_name = "shared/forms/widgets/checkbox_input.html"
    default_css_class = "form-check-input"


class Select(BaseCustomWidget, forms.Select):
    template_name = "shared/forms/widgets/select.html"
    default_css_class = "form-select"


class NullBooleanSelect(BaseCustomWidget, forms.NullBooleanSelect):
    template_name = "shared/forms/widgets/null_boolean_select.html"
    default_css_class = "form-select"


class SelectMultiple(BaseCustomWidget, forms.SelectMultiple):
    template_name = "shared/forms/widgets/select_multiple.html"
    default_css_class = "form-select"


class RadioSelect(BaseCustomWidget, forms.RadioSelect):
    template_name = "shared/forms/widgets/radio_select.html"
    default_css_class = "form-check-input"


class CheckboxSelectMultiple(BaseCustomWidget, forms.CheckboxSelectMultiple):
    template_name = "shared/forms/widgets/checkbox_select_multiple.html"
    default_css_class = "form-check-input"


class MultiWidget(BaseCustomWidget, forms.MultiWidget):
    template_name = "shared/forms/widgets/multi_widget.html"


class SplitDateTimeWidget(BaseCustomWidget, forms.SplitDateTimeWidget):
    template_name = "shared/forms/widgets/split_datetime_widget.html"


class SplitHiddenDateTimeWidget(BaseCustomWidget, forms.SplitHiddenDateTimeWidget):
    template_name = "shared/forms/widgets/split_hidden_datetime_widget.html"


class SelectDateWidget(BaseCustomWidget, forms.SelectDateWidget):
    template_name = "shared/forms/widgets/select_date_widget.html"
