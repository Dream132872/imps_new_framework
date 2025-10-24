"""
Custom implementation for form fields.
"""

from __future__ import annotations
from functools import lru_cache

from django import forms as django_forms
from django.contrib.contenttypes.models import ContentType

from core.application.dtos import PictureDTO
from core.application.queries.picture_queries import *
from shared.application.cqrs import dispatch_query

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
    "PictureField",
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
        self.hidden = kwargs.pop("hidden", False)
        self.form = None

        if self.hidden:
            kwargs["widget"] = HiddenInput

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
        kwargs.setdefault("required", False)
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


class PictureField(Field):
    """
    This is a new filed to manage pictures.
    """

    def __init__(
        self,
        object_id_field: str,
        app_label: str | None = None,
        model_name: str | None = None,
        picture_type: str = "main",
        many: bool = False,
        *args,  # type: ignore
        **kwargs,  # type: ignore
    ) -> None:
        kwargs.setdefault("widget", SelectPicture)
        kwargs["required"] = False
        self.object_id = None
        # should manage multiple image or not
        self.many = many
        # type of the picture (contains all picture types in picture model)
        self.picture_type = picture_type
        # app_label and model_name to get right ContentType instance
        self.app_label = app_label
        self.model_name = model_name

        # current picture (if it's not many)
        self.current_picture = None
        # current pictures (if it's many)
        self.current_pictures = []

        # object_id field
        self.object_id_field = object_id_field

        super().__init__(*args, **kwargs)

    def get_bound_field(
        self, form: django_forms.BaseForm, field_name: str
    ) -> django_forms.BoundField:
        bound_field = super().get_bound_field(form, field_name)
        bound_field.content_type = self.content_type
        bound_field.picture = self.picture
        bound_field.pictures = self.pictures
        bound_field.many = self.many
        bound_field.picture_type = self.picture_type
        self.object_id = form[getattr(self, "object_id_field")].initial

        return bound_field

    @lru_cache
    def content_type(self) -> ContentType | None:
        if self.app_label and self.model_name:
            return ContentType.objects.get_by_natural_key(
                app_label=self.app_label, model=self.model_name
            )

        return None

    @lru_cache
    def picture(self) -> PictureDTO | None:
        content_type = self.content_type()

        return dispatch_query(
            SearchFirstPictureQuery(
                picture_type=self.picture_type,
                content_type_id=content_type.id if content_type else None,
                object_id=self.object_id,
            )
        )

    @lru_cache
    def pictures(self) -> list[PictureDTO]:
        content_type = self.content_type()

        return dispatch_query(
            SearchPictureQuery(
                picture_type=self.picture_type,
                content_type_id=content_type.id if content_type else None,
                object_id=self.object_id,
            )
        )
