"""
User domain repository interface.
"""

from abc import abstractmethod

from core.domain.entities import User
from shared.domain.repositories import Repository

__all__ = ("UserRepository",)


class UserRepository(Repository[User]):
    """
    User repository interface.
    """
    pass
