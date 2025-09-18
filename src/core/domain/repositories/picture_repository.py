"""
Picture domain repository interface.
"""

from abc import ABC, abstractmethod

from core.domain.entities import Picture
from shared.domain.repositories import Repository

__all__ = ("PictureRepository",)


class PictureRepository(Repository[Picture]):
    """
    Picture repository interface.
    """

    pass
