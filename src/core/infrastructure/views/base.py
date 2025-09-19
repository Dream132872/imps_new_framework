import logging
from dataclasses import asdict
from typing import Any

from adrf.requests import AsyncRequest
from adrf.views import APIView
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from rest_framework import status
from rest_framework.response import Response

from core.application.queries import *
from shared.application.cqrs import dispatch_query_async
from shared.infrastructure.views import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/admin/home.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        from django.utils import translation
        from django.conf import settings

        translation.activate("fa")
        print(f"Current language: {translation.get_language()}")
        print(f"LOCALE_PATHS: {settings.LOCALE_PATHS}")
        print(f"translation of Dashboard: {translation.gettext('Dashboard')}")
        return super().get(request, *args, **kwargs)
