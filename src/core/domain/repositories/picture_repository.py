"""
Picture domain repository interface.
"""

import uuid
from abc import abstractmethod

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
        """Search pictures based on inputs.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | uuid.UUID | None, optional): id of the object in related item. Defaults to None.
            picture_type (str, optional): type of the picture (main, avatar, ...). Defaults to "".

        Returns:
            list[Picture]: list of pictures
        """

    @abstractmethod
    def is_valid_picture_type(self, picture_type: str) -> bool:
        """Checks that the picture type is valid or not based on model picture type text choices.

        Args:
            picture_type (str): type of the picture (for main, avatar, etc.)

        Returns:
            bool: is it ok to use this picture type or not.
        """

    @abstractmethod
    def search_first_picture(
        self,
        content_type: int | None = None,
        object_id: int | uuid.UUID | None = None,
        picture_type: str = "",
    ) -> Picture | None:
        """Search pictures based on inputs and return the first item.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | uuid.UUID | None, optional): id of the object in related item. Defaults to None.
            picture_type (str, optional): type of the picture (main, avatar, ...). Defaults to "".

        Returns:
            Picture | None: an instance of Picture entity.
        """
