from typing import Any, Callable, Dict, Optional

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import SafeText, mark_safe

__all__ = ("Form", "ModelForm")


class Form(forms.Form):
    """
    Custom Form class with enhanced functionality
    """

    # Custom form template
    template_name = "shared/forms/form.html"

    # Form styling
    css_class = "custom-form"

    # Form attributes
    form_attrs = {}

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        # Extract custom parameters
        self.template_name = kwargs.pop("template_name", self.template_name)
        self.css_class = kwargs.pop("css_class", self.css_class)
        self.form_attrs = kwargs.pop("form_attrs", self.form_attrs)

        super().__init__(*args, **kwargs)

        # Apply custom styling to all fields
        self._apply_custom_styling()

    def _apply_custom_styling(self):
        """Apply custom styling to all form fields"""
        for field_name, field in self.fields.items():
            # Set field-specific attributes
            if hasattr(field.widget, "required"):
                field.widget.required = field.required

            # Add field name as CSS class for styling
            if hasattr(field.widget, "attrs"):
                current_class = field.widget.attrs.get("class", "")
                css_field_name = field_name.replace("_", "-")
                field.widget.attrs["class"] = (
                    f"{current_class} field-{css_field_name}".strip()
                )

    def render_form(self, request=None, **context) -> SafeText:  # type: ignore
        """Render the entire form using custom template"""
        form_context = {
            "form": self,
            "form_class": self.css_class,
            "request": request,
        }
        form_context.update(context)

        return mark_safe(render_to_string(self.template_name, form_context))

    def get_field_html(self, field_name: str, **kwargs) -> str:  # type: ignore
        """Get HTML for a specific field"""
        if field_name not in self.fields:
            return ""

        field = self.fields[field_name]
        bound_field = self[field_name]

        context = {
            "field": bound_field,
            "field_name": field_name,
            "field_errors": bound_field.errors,
            "field_value": bound_field.value(),
        }
        context.update(kwargs)

        return mark_safe(render_to_string("shared/forms/field.html", context))

    def add_custom_validation(self, field_name: str, validator_func: Callable) -> None:
        """Add custom validation to a field"""

        def wrapper(value: Any) -> Any:
            try:
                return validator_func(value)
            except Exception as e:
                raise forms.ValidationError(str(e))

        if field_name in self.fields:
            self.fields[field_name].validators.append(wrapper)  # type: ignore

    def get_form_data(self) -> Dict[str, Any]:
        """Get cleaned form data as dictionary"""
        if self.is_valid():
            return self.cleaned_data
        return {}

    def has_field_error(self, field_name: str) -> bool:
        """Check if a specific field has errors"""
        return field_name in self.errors

    def get_field_error(self, field_name: str) -> Optional[str]:
        """Get the first error for a specific field"""
        if field_name in self.errors:
            return self.errors[field_name][0]  # type: ignore
        return None


class ModelForm(forms.ModelForm):
    """
    Custom ModelForm class with enhanced functionality
    """

    # Custom form template
    template_name = "shared/forms/form.html"

    # Form styling
    css_class = "custom-model-form"

    # Form attributes
    form_attrs = {}

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        # Extract custom parameters
        self.template_name = kwargs.pop("template_name", self.template_name)
        self.css_class = kwargs.pop("css_class", self.css_class)
        self.form_attrs = kwargs.pop("form_attrs", self.form_attrs)

        super().__init__(*args, **kwargs)

        # Apply custom styling to all fields
        self._apply_custom_styling()

    def _apply_custom_styling(self):
        """Apply custom styling to all form fields"""
        for field_name, field in self.fields.items():
            # Set custom attributes if not already set
            if hasattr(field.widget, "css_class") and not field.widget.css_class:
                field.widget.css_class = f"form-control"

            # Set field-specific attributes
            if hasattr(field.widget, "required"):
                field.widget.required = field.required

            # Add field name as CSS class for styling
            if hasattr(field.widget, "attrs"):
                current_class = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (
                    f"{current_class} field-{field_name}".strip()
                )

    def render_form(self, request=None, **context) -> SafeText:  # type: ignore
        """Render the entire form using custom template"""
        form_context = {
            "form": self,
            "form_class": self.css_class,
            "form_attrs": self.form_attrs,
            "request": request,
        }
        form_context.update(context)

        return mark_safe(render_to_string(self.template_name, form_context))

    def get_field_html(self, field_name: str, **kwargs) -> str:  # type: ignore
        """Get HTML for a specific field"""
        if field_name not in self.fields:
            return ""

        field = self.fields[field_name]
        bound_field = self[field_name]

        context = {
            "field": bound_field,
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

    def get_form_data(self) -> Dict[str, Any]:
        """Get cleaned form data as dictionary"""
        if self.is_valid():
            return self.cleaned_data
        return {}

    def has_field_error(self, field_name: str) -> bool:
        """Check if a specific field has errors"""
        return field_name in self.errors

    def get_field_error(self, field_name: str) -> Optional[str]:
        """Get the first error for a specific field"""
        if field_name in self.errors:
            return self.errors[field_name][0]  # type: ignore
        return None

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
