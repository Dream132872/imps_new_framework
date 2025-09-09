from shared.domain.entities import AggregateRoot

__all__ = ("User",)


class User(AggregateRoot):
    def __init__(self, id: str | None, username: str):
        super().__init__(id)
        self.username = username
