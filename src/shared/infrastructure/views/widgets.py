"""
This file contains widget structure.
each widget is a placeholder in html template that contains several components.
"""

import abc
from collections import namedtuple
from typing import Any, Dict, List, Optional, Tuple

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

__all__ = (
    "TemplateComponentBase",
    "TemplateComponent",
    "TemplateComponentBinder",
    "TemplateComponentPool",
)

TemplateComponentBinder = namedtuple(
    "TemplateComponentBinder", "widget_name display_order"
)


class TemplateComponentBase(abc.ABC):
    """
    Abstract base class for template components.
    """


class TemplateComponentPool:
    """
    Manages all template components in whole.
    """

    components: list["TemplateComponent"] = []
    """list of all template components"""

    @staticmethod
    def register_component(component: "TemplateComponent"):
        """
        This decorator is used to register a template component.
        """

        component_obj = component.as_component()
        TemplateComponentPool.components.append(component_obj)
        return component

    @staticmethod
    def get_widget_s_template_components(
        widget_name: str = "",
    ) -> list["TemplateComponent"]:
        """
        Gets list of template components for specific widget by name.
        """

        selected_components = filter(
            lambda a: len(
                list(filter(lambda b: b.widget_name == widget_name, a.widgets))
            )
            > 0,
            TemplateComponentPool.components,
        )
        return list(
            sorted(
                selected_components,
                key=lambda c: c.get_widget_binder(widget_name).display_order,  # type: ignore
            )
        )

    @staticmethod
    def render_components(request: HttpRequest, components: list["TemplateComponent"]):
        """
        Renders all template components with given request.
        """

        return mark_safe(
            "".join(list(map(lambda c: c.render(request=request) or "", components)))
        )


class TemplateComponent(TemplateComponentBase):
    """
    This class is the main widget component class that will be rendered as ordered in specified widgets.

    usage sample:

    make components.py module or components package in your plugin.
    in each module, create components like this:

    @TemplateComponentPool.register_component
    class Component(TemplateComponent):
        title = _('Custom component')
        template_name = 'file_path.html'
        widgets = [TemplateComponentBinder(widget_name='', display_order=1)]


    in template:
    load samo_widgets. then use it like this ->

    {% widget_renderer name='widget_name' %}

    """

    title: str = ""
    """title of the component"""

    widgets: list[TemplateComponentBinder] = []
    """list of widgets that this component should rendered into it"""

    template_name = ""
    """the name of the template that this component uses to render its content"""

    _cached_context: dict[str, Any] = {}
    """component context will be cached after first get_context call"""

    def render(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> Optional[str]:
        # check if should this component rendered for this request or not
        if not self.check_render_permission():
            return ""

        # get context data
        context: Optional[dict] = self.get_context_data() or {}
        context["request"] = request

        # get template name
        template_name = self.get_template_name() or self.template_name

        if not template_name:
            raise ImproperlyConfigured(
                "You should set template_name or override get_template_name to configure template structure"
            )

        if context:
            return render_to_string(
                self.get_template_name() or self.template_name, context, request
            )

        return None

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gets the data that this component uses to render"""
        return {}

    def get_template_name(self) -> str:
        """Get name of the template that this component uses to render"""
        return ""

    def check_render_permission(self) -> bool:
        """Checks that this component can be rendered with conditions or not"""
        return True

    def get_widget_binder(self, widget_name: str) -> Optional[TemplateComponentBinder]:
        res: List[TemplateComponentBinder] = list(
            filter(lambda a: a.widget_name == widget_name, self.widgets)
        )
        return res[0] if res else None

    @classmethod
    def as_component(cls) -> "TemplateComponent":
        component = cls()
        return component
