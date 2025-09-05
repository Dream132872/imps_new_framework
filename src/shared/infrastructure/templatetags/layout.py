"""
These are all layout default template tags.
"""

from ast import Tuple
from typing import Any, Dict
from django import template
from django.utils import timezone

register = template.Library()


@register.inclusion_tag(
    "samo/templatetags/layout/admin_site_header.html", takes_context=True
)
def admin_site_header(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin header inclusion
    """

    return {"navbar_items": []}


@register.inclusion_tag(
    "samo/templatetags/layout/admin_sidebar.html", takes_context=True
)
def admin_sidebar(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin sidebar inclusion
    """

    return {"menu_items": []}


@register.inclusion_tag(
    "samo/templatetags/layout/admin_fixed_footer.html", takes_context=True
)
def admin_fixed_footer(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin fixed footer inclusion
    """

    return {"current_year": timezone.now().year}
