"""
Authentication and authorization views.
"""

from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from core.infrastructure.forms.auth import LoginForm
from shared.infrastructure import views
from django.urls import reverse_lazy


class LoginView(views.ViewTitleMixin, views.FormView):
    page_title = _("Login")
    form_class = LoginForm
    template_name = "core/auth/login.html"
    # success_url = reverse_lazy("core:base:home")

    def form_valid(self, form: LoginForm) -> HttpResponse:
        print(form.get_form_data())
        form.add_error(None, "No user found")
        return self.form_invalid(form)
