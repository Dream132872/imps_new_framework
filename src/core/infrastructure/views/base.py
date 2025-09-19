import logging
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
