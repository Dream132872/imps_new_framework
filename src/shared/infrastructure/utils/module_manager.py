"""
Base structuer to load modules.
"""

import importlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

__all__ = ("ModuleNode", "load_module")


@dataclass
class ModuleNode:
    name: str
    """name of the file/folder."""

    content: str = ""
    """content of the node if it is file."""

    parent_dir: str = ""
    """this is parent directory of node. it contains BASE_DIR automatically."""

    children: list["ModuleNode"] = field(default_factory=list)
    """list of children nodes."""

    parent_module_node: Optional["ModuleNode"] = field(default=None)
    """parent node."""

    def __post_init__(self):
        for child in self.children:
            child.parent_module_node = self

    @property
    def full_path(self) -> Path:
        return Path(os.path.join(settings.BASE_DIR, self.parent_dir, self.name))

    def render(self, parent_dir: Optional[str] = None) -> None:
        """render the node."""

        if parent_dir:
            self.parent_dir = parent_dir

        if self.parent_dir and not self.content and len(self.name.split(".")) == 1:
            self.full_path.mkdir(exist_ok=True, parents=True)

        if len(self.name.split(".")) > 1 and not self.children:
            if not os.path.exists(str(self.full_path)):
                with open(str(self.full_path), "w") as file:
                    file.write(self.content)

        for child in self.children:
            child.render(parent_dir=str(self.full_path))


def load_module(module_dot_path: str) -> None:
    """
    this method gets dotted path of module.
    if it is just a single module, loads that but if it is a package, loads all its submodules and so on.
    """
    path = Path(settings.BASE_DIR, *module_dot_path.split("."))

    # check that the dotted path is for directory or just single
    if os.path.isdir(path):
        for iter_path, iter_dir_names, iter_file_names in path.walk(top_down=True):
            if "__pycache__" not in str(iter_path):
                for module in iter_file_names:
                    module_dotted_path = ".".join(
                        str(Path(iter_path, module))
                        .split(f"{settings.BASE_DIR}")[1]
                        .split("\\")[1:]
                    ).split(".py")[0]
                    try:
                        importlib.import_module(module_dotted_path)
                    except ImportError as e:
                        continue
    else:
        try:
            importlib.import_module(module_dot_path)
        except ImportError as e:
            pass
