from core.domain.entities import User
from shared.domain.repositories import Repository

__all__ = ("UserRepository",)


class UserRepository(Repository[User]):
    pass
