"""
Picture domain repository interface.
"""

import uuid
from abc import abstractmethod

from media.domain.entities import Picture
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
        object_id: int | str | None = None,
        picture_type: str = "",
    ) -> list[Picture]:
        """Search pictures based on inputs.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | str | None, optional): id of the object in related item. Defaults to None.
            picture_type (str, optional): type of the picture (main, avatar, ...). Defaults to "".

        Returns:
            list[Picture]: list of pictures
        """

    @abstractmethod
    def search_first_picture(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
        picture_type: str = "",
    ) -> Picture | None:
        """Search pictures based on inputs and return the first item.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | str | None, optional): id of the object in related item. Defaults to None.
            picture_type (str, optional): type of the picture (main, avatar, ...). Defaults to "".

        Returns:
            Picture | None: an instance of Picture entity.
        """

