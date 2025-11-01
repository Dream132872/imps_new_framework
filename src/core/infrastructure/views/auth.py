"""
Authentication and authorization views.
"""

from typing import Any

from django.contrib.auth import alogout, authenticate, login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from core.infrastructure.forms.auth import LoginForm
from shared.infrastructure import views


class LoginView(views.ViewTitleMixin, views.FormView):
    page_title = _("Login")
    form_class = LoginForm
    template_name = "core/auth/login.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(reverse("core:base:home"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: LoginForm) -> HttpResponse:
        next_url = self.request.GET.get("next", "")
        data = form.get_form_data()
        try:
            user = authenticate(
                request=self.request,
                username=data["username"],
                password=data["password"],
            )

            if user:
                if user.is_active:
                    if user.is_staff:
                        login(request=self.request, user=user)
                        if next_url and url_has_allowed_host_and_scheme(
                            next_url, allowed_hosts=[self.request.get_host()]
                        ):
                            return redirect(next_url)
                        return redirect(reverse("core:base:home"))
                    else:
                        form.add_error(None, _("You dont have enough permissions"))
                else:
                    form.add_error(None, _("You'r account is not activated"))
            else:
                form.add_error(None, _("There is no user with these credentials"))
        except PermissionDenied as e:
            form.add_error(None, str(e))
        except Exception as e:
            raise

        return self.form_invalid(form)


class LogoutView(views.View):
    async def get(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        user = await request.auser()
        if user.is_authenticated:
            await alogout(request)

        return redirect(reverse("core:auth:login"), permanent=True)
