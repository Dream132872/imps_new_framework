"""
Attachment domain repository interface.
"""

from abc import abstractmethod

from media.domain.entities import Attachment
from shared.domain.repositories import Repository

__all__ = ("AttachmentRepository",)


class AttachmentRepository(Repository[Attachment]):
    """
    Attachment repository interface.
    """

    @abstractmethod
    def search_attachments(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
    ) -> list[Attachment]:
        """Search attachments based on inputs.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | str | None, optional): id of the object in related item. Defaults to None.

        Returns:
            list[Attachment]: list of attachments
        """

    @abstractmethod
    def search_first_attachment(
        self,
        content_type: int | None = None,
        object_id: int | str | None = None,
    ) -> Attachment | None:
        """Search attachments based on inputs and return the first item.

        Args:
            content_type (int | None, optional): django app content_type. Defaults to None.
            object_id (int | str | None, optional): id of the object in related item. Defaults to None.

        Returns:
            Attachment | None: an instance of Attachment entity.
        """

