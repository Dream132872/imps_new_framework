from shared.domain.entities import AggregateRoot

__all__ = ("User",)


class User(AggregateRoot):
    def __init__(self, id: str | None, username: str):
        super().__init__(id)
        self._username = username

    @property
    def username(self) -> str:
        return self._username

    def __str__(self):
        return self.username

    def __repr__(self) -> str:
        return str(self)
