"""
User domain repository interface.
"""

from abc import abstractmethod

from identity.domain.entities import User
from shared.domain.pagination import DomainPaginator
from shared.domain.repositories import Repository

__all__ = ("UserRepository",)


class UserRepository(Repository[User]):
    """
    User repository interface.
    """

    @abstractmethod
    def search_users(
        self,
        full_name: str = "",
        email: str = "",
        username: str = "",
        page: int = 1,
        page_size: int = 25,
    ) -> DomainPaginator[User]:
        """
        Filter users based on filter params.

        Args:
            full_name (str): Filter based on user fullname.
            email (str): Filter based on user email.
            username (str): Filter based on user username.
            page (int): Page number for pagination (1-based).
            page_size (int): Number of items per page.

        Returns:
            DomainPaginator[User]: Paginated result containing users and metadata.
            list[User]: List of all users
        """
        pass

