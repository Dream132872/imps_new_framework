"""
This file contains menu item
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Literal

from shared.utils.singleton import SingletonClass

__all__ = ("PluginMenuItem", "PluginMenuPool", "MenuPositionEnum")


class MenuPositionEnum(Enum):
    SIDEBAR = "sidebar"
    NAVBAR = "navbar"


@dataclass()
class PluginMenuItem:
    """
    This is plugin menu item.

    after initializing a new instance of this class, it automatically adds the instance
    to the PluginMenuPool.
    """

    name: str
    """system name of the menu item"""

    title: str
    """title of the menu item"""

    url: str = ""
    """url of the menu item"""

    icon: str = ""
    """icon of the menu item"""

    parent_name: str | None = field(default=None)
    """system name of the parent menu item"""

    menu_position: MenuPositionEnum = MenuPositionEnum.SIDEBAR
    """position of the menu item ( sidebar or navbar )"""

    display_order: int = 0
    """display order of the menu item"""

    children: list["PluginMenuItem"] = field(default_factory=list)
    """list of children menu items"""

    def __post_init__(self):
        plugin_menu_pool = PluginMenuPool()
        plugin_menu_pool.add(self)

    def add(self, item: "PluginMenuItem") -> None:
        """add child item to the menu"""
        self.children.append(item)

    @property
    def is_active(self) -> Literal[False]:
        return False


@dataclass()
class PluginMenuPool(SingletonClass):
    _menus: ClassVar[dict[str, PluginMenuItem]] = {}
    """manage list of all menu items"""

    def add(self, item: "PluginMenuItem") -> None:
        """adds a menu item to the pool"""
        if item.name not in self._menus:
            self._menus[item.name] = item
        else:
            raise KeyError(f"Menu item {item.name} already exists")

    @property
    def menus(self) -> dict[str, PluginMenuItem]:
        return self._menus

    def get_menus_by_position(self, position: MenuPositionEnum) -> list[PluginMenuItem]:
        ordered_sidebar_items = list(
            filter(
                lambda x: x.menu_position == position,
                sorted(self._menus.values(), key=lambda x: x.display_order),
            )
        )
        return list(filter(lambda x: x.parent_name is None, ordered_sidebar_items))
