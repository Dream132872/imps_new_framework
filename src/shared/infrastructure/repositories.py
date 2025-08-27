"""
Base repository implementation for infrastructure layer
"""

from typing import Dict, Generic, List, Optional, Type, TypeVar

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

    def get_all(self) -> List[T]:
        return [self._model_to_entity(e) for e in self.model_class.objects.all()]

    def delete(self, entity: T) -> None:
        try:
            model_instance = self.model_class.objects.get(pk=entity.id)
            model_instance.delete(keep_parents=True)
        except self.model_class.DoesNotExist:
            raise EntityNotFoundError(f"Entity with id {entity.id} not found")

    def exists(self, id: str) -> bool:
        return self.model_class.objects.filter(pk=id).exists()

    def _entity_to_model(self, entity: T) -> models.Model:
        """Convert domain entity to django model."""
        raise NotImplementedError

    def _model_to_entity(self, model: models.Model) -> T:
        """Convert django model to domain entity."""
        raise NotImplementedError
