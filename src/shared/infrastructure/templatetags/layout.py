"""
These are all layout default template tags.
"""

from ast import Tuple
from typing import Any

from django import template
from django.utils import timezone

from shared.infrastructure.utils.menu_utils import *

register = template.Library()
menu_pool = MenuPool()


@register.inclusion_tag(
    "shared/templatetags/layout/admin_site_header.html", takes_context=True
)
def admin_site_header(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[str, Any]:
    """
    Admin header inclusion
    """

    return {
        "navbar_items": menu_pool.get_menus_by_position(
            position=MenuPositionEnum.NAVBAR
        ),
        "request": context.get("request", None),
    }


@register.inclusion_tag(
    "shared/templatetags/layout/admin_sidebar.html", takes_context=True
)
def admin_sidebar(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[str, Any]:
    """
    Admin sidebar inclusion
    """

    return {
        "menu_items": menu_pool.get_menus_by_position(
            position=MenuPositionEnum.SIDEBAR
        ),
        "request": context.get("request", None),
    }


@register.inclusion_tag(
    "shared/templatetags/layout/admin_fixed_footer.html", takes_context=True
)
def admin_fixed_footer(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[str, Any]:
    """
    Admin fixed footer inclusion
    """

    return {
        "current_year": timezone.now().year,
        "request": context.get("request", None),
    }


@register.inclusion_tag(
    "shared/templatetags/layout/admin_header_messages_box.html", takes_context=True
)
def admin_header_messages_box(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[Any, Any]:
    """
    Admin header messages box inclusion.
    """
    return {"request": context.get("request", None)}


@register.inclusion_tag(
    "shared/templatetags/layout/admin_header_notifications_box.html", takes_context=True
)
def admin_header_notifications_box(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[Any, Any]:
    """
    Admin header notifications box inclusion.
    """
    return {"request": context.get("request", None)}


@register.inclusion_tag(
    "shared/templatetags/layout/admin_header_user_menu_box.html", takes_context=True
)
def admin_header_user_menu_box(
    context: dict[str, Any], *args: Tuple, **kwargs: dict[str, Any]
) -> dict[Any, Any]:
    """
    Admin header user menu box inclusion.
    """
    return {"request": context.get("request", None)}
