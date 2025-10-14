"""
manage picture views.
"""

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy

from core.infrastructure.forms.picture import UpsertPictureForm
from shared.infrastructure import views

logger = logging.getLogger(__file__)


class CreatePictureView(views.AdminGenericMixin, views.FormView):
    form_class = UpsertPictureForm
    template_name = "core/picture/picture_upsert.html"
    permission_required = []
    success_url = reverse_lazy("core:picture:create_picture")

    def get(self, request: HttpRequest, content_type: str, object_id: str, *args: str, **kwargs: Any) -> HttpResponse:  # type: ignore
        self._content_type = content_type
        self._object_id = object_id
        return super().get(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        print(self._content_type, self._object_id)

        initial = super().get_initial()
        return initial

    def form_valid(self, form: UpsertPictureForm) -> HttpResponse:
        return super().form_valid(form)

    def form_invalid(self, form: UpsertPictureForm):
        response = super().form_invalid(form)
        return response
