"""
This file contains all required django generic views as Custom generic views.
each generic view has its own implementation, therefore, you should use them instead of django's generic views.
"""

from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import generic as django_generics

from shared.application.cqrs import Command, dispatch_command
from shared.infrastructure.views.exceptions import ApplicationExceptionHandlerMixin

__all__ = (
    "View",
    "TemplateView",
    "FormView",
    "CreateView",
    "UpdateView",
    "DeleteView",
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


class CreateView(ApplicationExceptionHandlerMixin, django_generics.CreateView):
    """
    Custom implementation of CreateView.
    """


class UpdateView(ApplicationExceptionHandlerMixin, django_generics.UpdateView):
    """
    Custom implementation of UpdateView.
    """


class DeleteView(ApplicationExceptionHandlerMixin, django_generics.View):
    """
    Custom implementation of DeleteView.
    the url should take pk as url parameter.
    the command class should has pk input too.
    """

    command_class: type[Command]
    return_exc_response_as_json = True

    def post(self, request: HttpRequest, pk: int | str):
        command_obj = self.command_class(pk=pk)  # type: ignore
        res = dispatch_command(command_obj)
        return JsonResponse(
            {
                "details": {"pk": pk},
                "message": _("The requested information was successfully deleted"),
            }
        )


class RedirectView(ApplicationExceptionHandlerMixin, django_generics.RedirectView):
    """
    Custom implementation of RedirectView.
    """
