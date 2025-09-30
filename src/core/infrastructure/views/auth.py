"""
Authentication and authorization views.
"""

from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from core.infrastructure.forms.auth import LoginForm
from shared.infrastructure.views import AdminGenericMixin, FormView, ViewTitleMixin
from django.urls import reverse_lazy


class LoginView(ViewTitleMixin, FormView):
    page_title = _("Login")
    form_class = LoginForm
    template_name = "core/auth/login.html"
    # success_url = reverse_lazy("core:base:home")

    def form_valid(self, form: LoginForm):
        print(form.get_form_data())
        return super().form_valid(form)


