"""
This file contains a class that manage singleton pattern for specific classes using inheritance
"""

from threading import RLock
from typing import Any, Dict, Self, Tuple


class SingletonClass:
    """
    This class manages singleton pattern for specific classes using inheritance.
    to use it, create a class that inherits from SingletonClass.
    it automatically manages __new__ for creating only one instance
    """

    _instance = None
    """This is the single instance of a class"""

    def __new__(cls, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Self:
        with RLock():
            if cls._instance is None:
                cls._instance = super().__new__(cls, *args, **kwargs)

            return cls._instance
