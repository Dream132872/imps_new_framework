"""
Manage picture views.
"""

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy

from core.infrastructure.forms.picture import UpsertPictureForm
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreatePictureView(views.FormView):
    form_class = UpsertPictureForm
    template_name = "core/picture/picture_upsert.html"
    permission_required = []
    success_url = reverse_lazy("core:picture:create_picture")

    def form_valid(self, form: UpsertPictureForm) -> HttpResponse:
        return super().form_valid(form)

    def form_invalid(self, form: UpsertPictureForm) -> HttpResponse:
        response = super().form_invalid(form)
        return response


class UpdatePictureView(views.FormView):
    form_class = UpsertPictureForm
    template_name = "core/picture/picture_upsert.html"
    permission_required = []

    def get_initial(self) -> dict[str, Any]:
        picture_id = self.kwargs.get("picture_id")
        # picture =
        return super().get_initial()

    def form_valid(self, form: UpsertPictureForm) -> JsonResponse:
        return JsonResponse({"status": "success"})

    def form_invalid(self, form: UpsertPictureForm) -> JsonResponse:
        return JsonResponse({"status": "error"})
