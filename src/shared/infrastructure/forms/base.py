from typing import Any, Callable

from django import forms
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import SafeText, mark_safe

__all__ = ("Form", "ModelForm")


class Form(forms.Form):
    """
    Custom Form class with enhanced functionality.
    """

    # Custom form template
    template_name = "shared/forms/form.html"
    # Form styling
    css_class = "custom-form"
    # Form attributes
    form_attrs = {
        # handle form parsley validation
        "data-parsley-validate": True,
        "data-parsley-ui-enabled": "true",
        "data-parsley-focus": "first",
    }
    # Method
    method = "post"
    # Form title
    form_title = ""
    # form action url
    form_action_url = ""
    # form id
    form_id = ""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        # Extract custom parameters
        self.template_name = kwargs.pop("template_name", self.template_name)
        self.css_class = kwargs.pop("css_class", self.css_class)
        self.form_attrs = kwargs.pop("form_attrs", self.form_attrs)

        super().__init__(*args, **kwargs)

        if self.get_form_action_url():
            self.form_attrs["action"] = self.get_form_action_url()

        # Apply custom styling to all fields
        self._apply_custom_styling()

    def _apply_custom_styling(self) -> None:
        """Apply custom styling to all form fields."""

        for field_name, field in self.fields.items():
            # bound field
            bound_field = self[field_name]

            # set form instance for each field
            if hasattr(field, "form"):
                field.form = self

            # Set field-specific attributes
            if hasattr(field.widget, "required"):
                field.widget.required = field.required

            # Set bound field object to widget
            if hasattr(field.widget, "field"):
                field.widget.field = field
                field.widget.bound_field = bound_field

            # Add field name as CSS class for styling
            if hasattr(field.widget, "attrs"):
                css_field_name = field_name.strip()

                # set the parsley treigger event for this widget
                if not field.widget.attrs.get("data-parsley-trigger"):
                    field.widget.attrs["data-parsley-trigger"] = "input focusout"

                # set the parsley validation threshold
                if not field.widget.attrs.get("data-parsley-validation-threshold"):
                    field.widget.attrs["data-parsley-validation-threshold"] = "0"

                field.widget.add_css_classes(f"input__{css_field_name}")

    def generate_flattened_attrs(self) -> SafeText:
        """Generated flatten attributes for form.

        Returns:
            str: flatten attributes.
        """

        if not "id" in self.form_attrs:
            self.form_attrs["id"] = self.get_form_id()

        return flatatt(attrs={key: value for key, value in self.form_attrs.items()})

    def render_form(self, request=None, **context) -> SafeText:  # type: ignore
        """Render the entire form using custom template."""
        # Try to get request from context if not provided
        if request is None:
            request = context.get("request")

        form_context = {
            "form": self,
            "form_class": self.css_class,
            "form_title": self.get_form_title(),
            "flattened_attrs": self.flattened_attrs,
            "request": request,
            "method": self.method,
        }
        form_context.update(context)

        return mark_safe(
            render_to_string(
                self.template_name, form_context, request=form_context["request"]
            )
        )

    def get_field_html(self, field_name: str, **kwargs) -> str:  # type: ignore
        """Get HTML for a specific field."""
        if field_name not in self.fields:
            return ""

        field = self.fields[field_name]
        bound_field = self[field_name]

        context = {
            "field": field,
            "bound_field": bound_field,
            "field_name": field_name,
            "field_errors": bound_field.errors,
            "field_value": bound_field.value(),
        }
        context.update(kwargs)

        return mark_safe(render_to_string("shared/forms/field.html", context))

    def add_custom_validation(self, field_name: str, validator_func: Callable) -> None:
        """Add custom validation to a field."""

        def wrapper(value: Any) -> Any:
            try:
                return validator_func(value)
            except Exception as e:
                raise forms.ValidationError(str(e))

        if field_name in self.fields:
            self.fields[field_name].validators.append(wrapper)  # type: ignore

    def get_form_data(self) -> dict[str, Any]:
        """Get cleaned form data as dictionary."""
        if self.is_valid():
            return self.cleaned_data
        return {}

    def get_form_action_url(self) -> str:
        return self.form_action_url

    def has_field_error(self, field_name: str) -> bool:
        """Check if a specific field has errors."""
        return field_name in self.errors

    def get_field_error(self, field_name: str) -> str | None:
        """Get the first error for a specific field."""
        if field_name in self.errors:
            return self.errors[field_name][0]  # type: ignore
        return None

    def get_form_title(self) -> str:
        return self.form_title

    def get_media(self) -> forms.Media:
        """Get all media files from form and all its widgets."""
        # Start with form's own media
        media = forms.Media()

        # Add form's own media
        if hasattr(self.__class__, "Media"):
            media += forms.Media(self.__class__.Media)

        # Add media from all widgets
        for field in self.fields.values():
            if hasattr(field.widget, "Media"):
                media += forms.Media(field.widget.__class__.Media)

        return media

    @property
    def media(self) -> forms.Media:
        """Return the media files for this form and all its widgets."""
        return self.get_media()

    @property
    def flattened_attrs(self) -> str:
        return self.generate_flattened_attrs()

    def get_form_id(self) -> str:
        return self.form_id


class ModelForm(forms.ModelForm):
    """
    Custom ModelForm class with enhanced functionality
    """

    # Custom form template
    template_name = "shared/forms/form.html"
    # Form styling
    css_class = "custom-form"
    # Form attributes
    form_attrs = {
        # handle form parsley validation
        "data-parsley-validate": True,
        "data-parsley-ui-enabled": "true",
        "data-parsley-focus": "first",
    }
    # Method
    method = "post"
    # Form title
    form_title = ""
    # form action url
    form_action_url = ""
    # form id
    form_id = ""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        # Extract custom parameters
        self.template_name = kwargs.pop("template_name", self.template_name)
        self.css_class = kwargs.pop("css_class", self.css_class)
        self.form_attrs = kwargs.pop("form_attrs", self.form_attrs)

        super().__init__(*args, **kwargs)

        if self.get_form_action_url():
            self.form_attrs["action"] = self.get_form_action_url()

        # Apply custom styling to all fields
        self._apply_custom_styling()

    def _apply_custom_styling(self) -> None:
        """Apply custom styling to all form fields and replace widgets with custom ones."""
        # Import widgets here to avoid circular imports
        from .widgets import (
            CheckboxInput,
            CheckboxSelectMultiple,
            ClearableFileInput,
            DateInput,
            DateTimeInput,
            EmailInput,
            FileInput,
            NumberInput,
            PasswordInput,
            RadioSelect,
            Select,
            SelectMultiple,
            SelectPicture,
            Textarea,
            TextInput,
            TimeInput,
            URLInput,
        )

        # Widget mapping for automatic widget replacement
        # Using actual Django widget class names
        widget_mapping = {
            "TextInput": TextInput,
            "EmailInput": EmailInput,
            "URLInput": URLInput,
            "NumberInput": NumberInput,
            "PasswordInput": PasswordInput,
            "DateInput": DateInput,
            "DateTimeInput": DateTimeInput,
            "TimeInput": TimeInput,
            "CheckboxInput": CheckboxInput,
            "Select": Select,
            "SelectMultiple": SelectMultiple,
            "RadioSelect": RadioSelect,
            "CheckboxSelectMultiple": CheckboxSelectMultiple,
            "Textarea": Textarea,
            "FileInput": FileInput,
            "ClearableFileInput": ClearableFileInput,
            "PictureField": SelectPicture,
        }

        for field_name, field in self.fields.items():
            # Replace default widgets with custom widgets
            current_widget_class = field.widget.__class__.__name__
            if current_widget_class in widget_mapping:
                custom_widget_class = widget_mapping[current_widget_class]
                # Preserve existing attributes
                attrs = field.widget.attrs.copy()
                field.widget = custom_widget_class(attrs=attrs)

            # Set field-specific attributes
            if hasattr(field.widget, "required"):
                field.widget.required = field.required

            # Set bound field object to widget
            if hasattr(field.widget, "field"):
                field.widget.field = self[field_name]

            # Add field name as CSS class for styling
            if hasattr(field.widget, "attrs"):
                css_field_name = field_name.strip()

                # set the parsley treigger event for this widget
                if not field.widget.attrs.get("data-parsley-trigger"):
                    field.widget.attrs["data-parsley-trigger"] = "input focusout"

                # set the parsley validation threshold
                if not field.widget.attrs.get("data-parsley-validation-threshold"):
                    field.widget.attrs["data-parsley-validation-threshold"] = "0"

                field.widget.add_css_classes(f"input__{css_field_name}")

    def generate_flattened_attrs(self) -> SafeText:
        """Generated flatten attributes for form.

        Returns:
            str: flatten attributes.
        """

        if not "id" in self.form_attrs:
            self.form_attrs["id"] = self.get_form_id()

        return flatatt(attrs={key: value for key, value in self.form_attrs.items()})

    def render_form(self, request=None, **context) -> SafeText:  # type: ignore
        """Render the entire form using custom template."""
        # Try to get request from context if not provided
        if request is None:
            request = context.get("request")

        form_context = {
            "form": self,
            "form_class": self.css_class,
            "form_title": self.get_form_title(),
            "flattened_attrs": self.generate_flattened_attrs(),
            "request": request,
            "method": self.method,
        }
        form_context.update(context)

        return mark_safe(
            render_to_string(
                self.template_name, form_context, request=form_context["request"]
            )
        )

    def get_field_html(self, field_name: str, **kwargs) -> str:  # type: ignore
        """Get HTML for a specific field"""
        if field_name not in self.fields:
            return ""

        field = self.fields[field_name]
        bound_field = self[field_name]

        context = {
            "field": field,
            "bound_field": bound_field,
            "field_name": field_name,
            "field_errors": bound_field.errors,
            "field_value": bound_field.value(),
        }
        context.update(kwargs)

        return mark_safe(render_to_string("shared/forms/field.html", context))

    def add_custom_validation(self, field_name: str, validator_func: Callable) -> None:
        """Add custom validation to a field"""

        def wrapper(value) -> Any:  # type: ignore
            try:
                return validator_func(value)
            except Exception as e:
                raise forms.ValidationError(str(e))

        if field_name in self.fields:
            self.fields[field_name].validators.append(wrapper)  # type: ignore

    def get_form_data(self) -> dict[str, Any]:
        """Get cleaned form data as dictionary."""
        if self.is_valid():
            return self.cleaned_data
        return {}

    def get_form_action_url(self) -> str:
        return self.form_action_url

    def has_field_error(self, field_name: str) -> bool:
        """Check if a specific field has errors."""
        return field_name in self.errors

    def get_field_error(self, field_name: str) -> str | None:
        """Get the first error for a specific field."""
        if field_name in self.errors:
            return self.errors[field_name][0]  # type: ignore
        return None

    def get_form_title(self) -> str:
        return self.form_title

    def get_media(self) -> forms.Media:
        """Get all media files from form and all its widgets."""
        # Start with form's own media
        media = forms.Media()

        # Add form's own media
        if hasattr(self.__class__, "Media"):
            media += forms.Media(self.__class__.Media)

        # Add media from all widgets
        for field in self.fields.values():
            if hasattr(field.widget, "Media"):
                media += forms.Media(field.widget.__class__.Media)

        return media

    @property
    def media(self) -> forms.Media:
        """Return the media files for this form and all its widgets."""
        return self.get_media()

    @property
    def flattened_attrs(self) -> str:
        return self.generate_flattened_attrs()

    def get_form_id(self) -> str:
        return self.form_id

    def save_with_commit(self, commit: bool = True, **kwargs) -> Any:  # type: ignore
        """Save the model instance with custom commit handling"""
        instance = super().save(commit=False)

        # Apply any custom modifications
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        if commit:
            instance.save()

        return instance
