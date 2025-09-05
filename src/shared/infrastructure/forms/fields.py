from django import forms as django_forms

__all__ = (
    'Field',
    'CharField'
)


class Field(django_forms.Field):
    """Custom implementation of Field"""


class CharField(django_forms.CharField):
    """Custom implementation of Field"""
