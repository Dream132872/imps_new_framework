"""
This file contains all required django generic views as Custom generic views.
each generic view has its own implementation, therefore, you should use them instead of django's generic views.
"""

from django.views import generic as django_generics
from shared.infrastructure.views.exceptions import ApplicationExceptionHandlerMixin

__all__ = (
    "View",
    "TemplateView",
    "FormView",
    "UpdateView",
    "RedirectView",
)


class View(ApplicationExceptionHandlerMixin, django_generics.View):
    """
    Custom implementation of View.
    """


class TemplateView(ApplicationExceptionHandlerMixin, django_generics.TemplateView):
    """
    Custom implementation of TemplateView.
    """


class FormView(ApplicationExceptionHandlerMixin, django_generics.FormView):
    """
    Custom implementation of FormView.
    """


class UpdateView(ApplicationExceptionHandlerMixin, django_generics.UpdateView):
    """
    Custom implementation of UpdateView.
    """


class RedirectView(ApplicationExceptionHandlerMixin, django_generics.RedirectView):
    """
    Custom implementation of RedirectView
    """
