"""
Template tags for custom forms
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def render_form(context, form, **kwargs):
    """
    Render a custom form with all its fields and styling
    """
    # Get request from template context
    request = context.get('request')

    return form.render_form(request=request, **kwargs)


@register.simple_tag
def render_field(form, field_name, **kwargs):
    """
    Render a specific field from a form
    """
    return form.get_field_html(field_name, **kwargs)


@register.filter
def has_error(form, field_name):
    """
    Check if a field has errors
    """
    return form.has_field_error(field_name)


@register.filter
def get_error(form, field_name):
    """
    Get the first error for a field
    """
    return form.get_field_error(field_name)
