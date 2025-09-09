"""
Base repository implementation for infrastructure layer
"""

from __future__ import annotations

from typing import Any, Dict, Generic, Hashable, List, Tuple, Type, TypeVar

from asgiref.sync import sync_to_async
from django.db import models, transaction

from shared.application.exceptions import ConfigurationError
from shared.domain.entities import Entity
from shared.domain.exceptions import *
from shared.domain.repositories import Repository, UnitOfWork

T = TypeVar("T", bound=Entity)
R = TypeVar("R", bound=Repository)


class DjangoRepository(Repository[T], Generic[T]):
    """Base django repository implementation"""

    def __init__(self, model_class: Type[models.Model], entity_class: Type[T]) -> None:
        self.model_class = model_class
        self.entity_class = entity_class

    def save(self, entity: T) -> T:
        model_instance = self._entity_to_model(entity)
        model_instance.save()
        return self._model_to_entity(model_instance)

    async def save_async(self, entity: T) -> T:
        return await sync_to_async(self.save)(entity=entity)

    def get_by_id(self, id: str) -> T | None:
        try:
            model_instance = self.model_class.objects.get(pk=id)
            return self._model_to_entity(model_instance)
        except self.model_class.DoesNotExist:
            return None

    async def get_by_id_async(self, id: str) -> T | None:
        return await sync_to_async(self.get_by_id)(id)

    def get_all(self) -> List[T]:
        return [
            self._model_to_entity(e)
            for e in self.model_class.objects.all()
        ]

    async def get_all_async(self) -> List[T]:
        return await sync_to_async(self.get_all)()

    def delete(self, entity: T) -> None:
        try:
            model_instance = self.model_class.objects.get(pk=entity.id)
            model_instance.delete(keep_parents=True)
        except self.model_class.DoesNotExist:
            raise EntityNotFoundError(f"Entity with id {entity.id} not found")

    async def delete_async(self, entity: T) -> None:
        await sync_to_async(self.delete)(entity=entity)

    def exists_by_id(self, id: str) -> bool:
        raise NotImplementedError

    async def exists_by_id_async(self, id: str) -> bool:
        return await self.model_class.objects.filter(pk=id).aexists()

    def _entity_to_model(self, entity: T) -> models.Model:
        """Convert domain entity to django model."""
        raise NotImplementedError

    def _model_to_entity(self, model: models.Model) -> T:
        """Convert django model to domain entity."""
        raise NotImplementedError


class DjangoUnitOfWork(UnitOfWork):
    """
    Django implementation of the Unit of Work.
    Each domain has it's own unit-of-work implementation that all of them should inherit this class.
    """

    def __init__(self) -> None:
        self._repositories = {}
        self._transaction = None

    def __enter__(self):
        self._transaction = transaction.atomic()
        self._transaction.__enter__()

    async def __aenter__(self) -> None:
        self._transaction = await sync_to_async(transaction.atomic)()
        await sync_to_async(self._transaction.__enter__)()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._transaction:
            self._transaction.__exit__(exc_type, exc_val, exc_tb)

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._transaction:
            await sync_to_async(self._transaction.__exit__)(exc_type, exc_val, exc_tb)

    async def commit_async(self) -> None:
        # django's transactions are automatically commited when the context exits
        pass

    async def rollback_async(self) -> None:
        if self._transaction:
            await sync_to_async(self._transaction.__exit__)(
                type(Exception("RollBack")), None, None
            )

    def get_repository(self, repo: Type[R]) -> R:
        if not repo in self._repositories:
            from shared.infrastructure.ioc import get_injector

            injector = get_injector()
            try:
                self._repositories[repo] = injector.get(repo)
            except:
                raise ConfigurationError(message=f"No repository registered for {repo}")

        return self._repositories[repo]

    def __getitem__(self, repo_type: Type[R]) -> R:
        return self.get_repository(repo_type)
