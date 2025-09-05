"""
Base repository implementation for infrastructure layer
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from asgiref.sync import sync_to_async
from django.db import models, transaction

from shared.domain.entities import Entity
from shared.domain.exceptions import *
from shared.domain.repositories import Repository, UnitOfWork

T = TypeVar("T", bound=Entity)


class DjangoRepository(Repository[T], Generic[T]):
    """Base django repository implementation"""

    def __init__(self, model_class: Type[models.Model], entity_class: Type[T]) -> None:
        self.model_class = model_class
        self.entity_class = entity_class

    async def save_async(self, entity: T) -> T:
        model_instance = self._entity_to_model(entity)
        await model_instance.asave()
        return self._model_to_entity(model_instance)

    async def get_by_id_async(self, id: str) -> T | None:
        try:
            model_instance = await self.model_class.objects.aget(pk=id)
            return self._model_to_entity(model_instance)
        except self.model_class.DoesNotExist:
            return None

    async def get_all_async(self) -> List[T]:
        return [
            self._model_to_entity(e)
            for e in await sync_to_async(self.model_class.objects.all)()
        ]

    async def delete_async(self, entity: T) -> None:
        try:
            model_instance = await self.model_class.objects.aget(pk=entity.id)
            await model_instance.adelete(keep_parents=True)
        except self.model_class.DoesNotExist:
            raise EntityNotFoundError(f"Entity with id {entity.id} not found")

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

    def get_repository(self, entity_type: type[T]) -> Repository[T]:
        if entity_type in self._repositories:
            return self._repositories[entity_type]

        raise NotImplementedError(f"No repository registered for {entity_type}")
