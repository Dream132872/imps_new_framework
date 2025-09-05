"""
These are all layout default template tags.
"""

from ast import Tuple
from typing import Any, Dict

from django import template
from django.utils import timezone

from shared.utils.menu_utils import *

register = template.Library()
menu_pool = MenuPool()


@register.inclusion_tag(
    "shared/templatetags/layout/admin_site_header.html", takes_context=True
)
def admin_site_header(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin header inclusion
    """

    return {
        "navbar_items": menu_pool.get_menus_by_position(
            position=MenuPositionEnum.NAVBAR
        )
    }


@register.inclusion_tag(
    "shared/templatetags/layout/admin_sidebar.html", takes_context=True
)
def admin_sidebar(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin sidebar inclusion
    """

    return {
        "menu_items": menu_pool.get_menus_by_position(position=MenuPositionEnum.SIDEBAR)
    }


@register.inclusion_tag(
    "shared/templatetags/layout/admin_fixed_footer.html", takes_context=True
)
def admin_fixed_footer(context: Dict[str, Any], *args: Tuple, **kwargs: Dict[str, Any]):
    """
    Admin fixed footer inclusion
    """

    return {"current_year": timezone.now().year}
