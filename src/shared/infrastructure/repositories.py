"""
Base repository implementation for infrastructure layer
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from shared.application.exceptions import ApplicationConfigurationError
from shared.domain.entities import Entity
from shared.domain.exceptions import *
from shared.domain.repositories import Repository, UnitOfWork

T = TypeVar("T", bound=Entity)
R = TypeVar("R", bound=Repository)


class DjangoRepository(Repository[T], Generic[T]):
    """Base django repository implementation"""

    def __init__(self, model_class: type[models.Model], entity_class: type[T]) -> None:
        self.model_class = model_class
        self.entity_class = entity_class

    def save(self, entity: T) -> T:
        model_instance = self._entity_to_model(entity)
        model_instance.save()
        return self._model_to_entity(model_instance)

    def get_by_id(self, id: str) -> T | None:
        try:
            model_instance = self.model_class.objects.get(pk=id)
            return self._model_to_entity(model_instance)
        except self.model_class.DoesNotExist:
            return None

    def get_all(self) -> list[T]:
        return [self._model_to_entity(e) for e in self.model_class.objects.all()]

    def delete(self, entity: T) -> None:
        try:
            model_instance = self.model_class.objects.get(pk=entity.id)
            model_instance.delete(keep_parents=True)
        except self.model_class.DoesNotExist:
            raise DomainEntityNotFoundError(
                _("Entity with id {entity_id} not found").format(entity_id=entity.id)
            )

    def exists_by_id(self, id: str) -> bool:
        return self.model_class.objects.filter(pk=id).exists()

    def _entity_to_model(self, entity: T) -> Any:
        """Convert domain entity to django model."""
        raise NotImplementedError

    def _model_to_entity(self, model: Any) -> T:
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

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._transaction:
            self._transaction.__exit__(exc_type, exc_val, exc_tb)

    def commit(self) -> None:
        # django's transactions are automatically commited when the context exits.
        pass

    def rollback(self) -> None:
        if self._transaction:
            self._transaction.__exit__(type(Exception("RollBack")), None, None)

    def _get_repository(self, repo: type[R]) -> R:
        if not repo in self._repositories:
            from shared.infrastructure.ioc import get_injector

            injector = get_injector()
            try:
                self._repositories[repo] = injector.get(repo)
            except:
                raise ApplicationConfigurationError(
                    message=f"No repository registered for {repo}"
                )

        return self._repositories[repo]

    def __getitem__(self, repo_type: type[R]) -> R:
        return self._get_repository(repo_type)
