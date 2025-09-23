"""
Authentication and authorization view.
"""

from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from shared.infrastructure.views import FormView


class LoginView(FormView):
    pass
