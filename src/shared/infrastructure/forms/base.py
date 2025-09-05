"""
This file contains base Form and ModelForm
"""

from django import forms

__all__ = (
    'Form',
    'ModelForm'
)


class Form(forms.Form):
    pass


class ModelForm(forms.ModelForm):
    pass
