from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import ContextMixin


class ViewTitleMixin(ContextMixin):
    """
    This mixin adds title to the context.
    you can use it via set title attribute or call get_title method.
    """

    page_title = ""

    def get_title(self):
        pass

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title() or self.page_title
        return context


class AdminGenericMixin(ViewTitleMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """
    This class contains basic mixins that every admin view should have like:
    PermissionRequiredMixin, ViewTitleMixin and AdminGenericViewMixin
    """
