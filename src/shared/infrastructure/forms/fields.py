"""
Custom implementation for form fields.
"""

from django import forms as django_forms

from .widgets import *

__all__ = (
    "Field",
    "CharField",
    "EmailField",
    "URLField",
    "IntegerField",
    "DecimalField",
    "FloatField",
    "BooleanField",
    "DateField",
    "DateTimeField",
    "TimeField",
    "FileField",
    "ImageField",
    "ChoiceField",
    "MultipleChoiceField",
    "ModelChoiceField",
    "ModelMultipleChoiceField",
)


class Field(django_forms.Field):
    """Custom implementation of Field with enhanced functionality."""

    widget = TextInput

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        # Extract custom parameters
        self.help_text = kwargs.get("help_text", "")
        self.placeholder = kwargs.pop("placeholder", "")
        self.css_class = kwargs.pop("css_class", "")
        self.required = kwargs.get("required", False)
        self.disabled = kwargs.get("disabled", False)
        self.readonly = kwargs.pop("readonly", False)

        super().__init__(*args, **kwargs)

        # Set widget attributes
        if hasattr(self.widget, "help_text") and self.help_text:
            self.widget.help_text = self.help_text
        if hasattr(self.widget, "placeholder") and self.placeholder:
            self.widget.placeholder = self.placeholder
        if hasattr(self.widget, "add_css_classes") and self.css_class:
            self.widget.add_css_classes(self.css_class)

        if self.disabled:
            self.widget.disabled = self.disabled

        if self.readonly:
            self.widget.readonly = self.readonly

        if self.required:
            self.widget.required = self.required


class CharField(Field, django_forms.CharField):
    """Custom CharField with TextInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", TextInput)
        super().__init__(*args, **kwargs)


class EmailField(Field, django_forms.EmailField):
    """Custom EmailField with EmailInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", EmailInput)
        super().__init__(*args, **kwargs)


class URLField(Field, django_forms.URLField):
    """Custom URLField with URLInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", URLInput)
        super().__init__(*args, **kwargs)


class IntegerField(Field, django_forms.IntegerField):
    """Custom IntegerField with NumberInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", NumberInput)
        super().__init__(*args, **kwargs)


class DecimalField(Field, django_forms.DecimalField):
    """Custom DecimalField with NumberInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", NumberInput)
        super().__init__(*args, **kwargs)


class FloatField(Field, django_forms.FloatField):
    """Custom FloatField with NumberInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", NumberInput)
        super().__init__(*args, **kwargs)


class BooleanField(Field, django_forms.BooleanField):
    """Custom BooleanField with CheckboxInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", CheckboxInput)
        super().__init__(*args, **kwargs)


class DateField(Field, django_forms.DateField):
    """Custom DateField with DateInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", DateInput)
        super().__init__(*args, **kwargs)


class DateTimeField(Field, django_forms.DateTimeField):
    """Custom DateTimeField with DateTimeInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", DateTimeInput)
        super().__init__(*args, **kwargs)


class TimeField(Field, django_forms.TimeField):
    """Custom TimeField with TimeInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", TimeInput)
        super().__init__(*args, **kwargs)


class FileField(Field, django_forms.FileField):
    """Custom FileField with FileInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", FileInput)
        super().__init__(*args, **kwargs)


class ImageField(Field, django_forms.ImageField):
    """Custom ImageField with FileInput widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", FileInput)
        super().__init__(*args, **kwargs)


class ChoiceField(Field, django_forms.ChoiceField):
    """Custom ChoiceField with Select widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", Select)
        super().__init__(*args, **kwargs)


class MultipleChoiceField(Field, django_forms.MultipleChoiceField):
    """Custom MultipleChoiceField with SelectMultiple widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", SelectMultiple)
        super().__init__(*args, **kwargs)


class ModelChoiceField(Field, django_forms.ModelChoiceField):
    """Custom ModelChoiceField with Select widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", Select)
        super().__init__(*args, **kwargs)


class ModelMultipleChoiceField(Field, django_forms.ModelMultipleChoiceField):
    """Custom ModelMultipleChoiceField with SelectMultiple widget"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        kwargs.setdefault("widget", SelectMultiple)
        super().__init__(*args, **kwargs)
