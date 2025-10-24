"""
Picture domain repository interface.
"""

from abc import ABC, abstractmethod
import uuid

from core.domain.entities import Picture
from shared.domain.repositories import Repository

__all__ = ("PictureRepository",)


class PictureRepository(Repository[Picture]):
    """
    Picture repository interface.
    """

    @abstractmethod
    def search_pictures(
        self,
        content_type: int | None = None,
        object_id: int | uuid.UUID | None = None,
        picture_type: str = "",
    ) -> list[Picture]:
        pass

    @abstractmethod
    def search_first_picture(
        self,
        content_type: int | None = None,
        object_id: int | uuid.UUID | None = None,
        picture_type: str = "",
    ) -> Picture | None:
        pass
