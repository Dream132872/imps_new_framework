"""
This file contains all required django generic views as Custom generic views.
each generic view has its own implementation, therefore, you should use them instead of django's generic views.
"""

from django.views import generic as django_generics

__all__ = (
    "View",
    "TemplateView",
    "FormView",
)


class View(django_generics.View):
    """
    Custom implementation of View.
    """


class TemplateView(django_generics.TemplateView):
    """
    Custom implementation of TemplateView.
    """


class FormView(django_generics.FormView):
    """
    Custom implementation of FormView.
    """
