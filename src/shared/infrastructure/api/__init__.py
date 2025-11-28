"""
Base configuration for api system using django ninja package.
"""

import ninja_extra
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import gettext_lazy as _

from .renderer import ORJSONRenderer

api_v1 = ninja_extra.NinjaExtraAPI(
    title=_("IMPS API documentation"),
    description=_("API Endpoints of IMPS system."),
    version="1.0.0",
    renderer=ORJSONRenderer(),
    docs_decorator=staff_member_required,
    urls_namespace="api_v1",
)
