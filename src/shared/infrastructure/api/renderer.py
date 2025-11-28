"""
Implement custom renderer for api.
"""

from typing import Any

import orjson
from django.http import HttpRequest
from ninja.renderers import BaseRenderer


class ORJSONRenderer(BaseRenderer):
    """
    ORJSON Renderer implementation for api.
    orjson is one of the fastest json renderer available for python.
    """

    media_type = "application/json"

    def render(self, request: HttpRequest, data: Any, *, response_status: Any) -> bytes:
        return orjson.dumps(data)
