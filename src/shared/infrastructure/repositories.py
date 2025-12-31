"""
Base repository implementation for infrastructure layer
"""

from __future__ import annotations

from typing import Any, Generic, Self, TypeVar

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from shared.application.exceptions import ApplicationConfigurationError
from shared.domain.entities import AggregateRoot, Entity
from shared.domain.exceptions import *
from shared.domain.repositories import Repository, UnitOfWork

T = TypeVar("T", bound=Entity)
R = TypeVar("R", bound=Repository)


class DjangoRepository(Repository[T], Generic[T]):
    """Base django repository implementation"""

    def __init__(self, model_class: type[models.Model], entity_class: type[T]) -> None:
        self.model_class = model_class
        self.entity_class = entity_class
        self._unit_of_work: UnitOfWork | None = None

    def set_unit_of_work(self, uow: UnitOfWork) -> None:
        """Set the unit of work for tracking aggregates.

        Args:
            uow: The unit of work instance to track aggregates with.
        """
        self._unit_of_work = uow

    def _track_aggregate(self, entity: T) -> None:
        """Track aggregate root for domain event publishing.

        Args:
            entity: The entity to track if it's an aggregate root.
        """
        if isinstance(entity, AggregateRoot) and self._unit_of_work:
            if hasattr(self._unit_of_work, "_track_aggregate"):
                self._unit_of_work._track_aggregate(entity)  # type: ignore

    def save(self, entity: T) -> T:
        if entity.id:
            try:
                # Try to get existing instance (single query)
                model_instance = self.model_class.objects.get(pk=entity.id)
                # Update existing instance
                updated_model = self._entity_to_model(entity)
                for field in model_instance._meta.fields:
                    field_name = field.name
                    if field_name in ("id", "created_at", "updated_at"):
                        continue
                    if hasattr(updated_model, field_name):
                        setattr(
                            model_instance,
                            field_name,
                            getattr(updated_model, field_name),
                        )
                model_instance.save()
            except self.model_class.DoesNotExist:
                # Entity doesn't exist, create new
                model_instance = self._entity_to_model(entity)
                model_instance.save()
        else:
            # No ID, create new
            model_instance = self._entity_to_model(entity)
            model_instance.save()
        saved_entity = self._model_to_entity(model_instance)
        self._track_aggregate(entity)
        return saved_entity

    def get_by_id(self, id: str) -> T:
        try:
            model_instance = self.model_class.objects.get(pk=id)
            return self._model_to_entity(model_instance)
        except self.model_class.DoesNotExist:
            raise DomainEntityNotFoundError(
                _("Entity with id {entity_id} not found").format(entity_id=id)
            )

    def get_all(self) -> list[T]:
        return [self._model_to_entity(e) for e in self.model_class.objects.all()]

    def delete(self, entity: T) -> None:
        try:
            model_instance = self.model_class.objects.get(pk=entity.id)
            self._track_aggregate(entity)
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
        self._transaction: transaction.Atomic | None = None
        self._should_rollback = False
        self._tracked_aggregates: set[AggregateRoot] = set()

    def __enter__(self) -> Self:
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        self._should_rollback = False
        self._tracked_aggregates.clear()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._transaction:
            # If rollback was explicitly requested, mark it
            if self._should_rollback:
                transaction.set_rollback(True)

            # Check if transaction will commit (no exception and no rollback)
            will_commit = exc_type is None and not self._should_rollback

            self._transaction.__exit__(exc_type, exc_val, exc_tb)

            # Publish domain events only after successful commit
            if will_commit:
                self._publish_domain_events()
        else:
            # If no transaction, still publish events (for testing scenarios)
            if exc_type is None:
                self._publish_domain_events()

        self._transaction = None
        self._should_rollback = False
        self._tracked_aggregates.clear()

    def commit(self) -> None:
        # Django's transactions are automatically committed when the context exits normally
        # This method is here for interface compliance, but Django handles it automatically
        pass

    def rollback(self) -> None:
        """Mark the transaction for rollback.

        The actual rollback will occur when the context exits.
        """
        if not self._transaction:
            raise RuntimeError("Cannot rollback: not in a transaction context")
        self._should_rollback = True
        transaction.set_rollback(True)

    def _track_aggregate(self, aggregate: AggregateRoot) -> None:
        """Track an aggregate root for domain event publishing.

        Args:
            aggregate: The aggregate root to track.
        """
        self._tracked_aggregates.add(aggregate)

    def _publish_domain_events(self) -> None:
        """Collect and publish all domain events from tracked aggregates.

        This method is called after a successful transaction commit.
        It collects all domain events from tracked aggregates, publishes them,
        and then clears the events from the aggregates.
        """
        from shared.domain.events import DomainEvent, get_event_bus

        if not self._tracked_aggregates:
            return

        event_bus = get_event_bus()
        all_events: list[DomainEvent] = []

        # Collect all events from tracked aggregates
        for aggregate in self._tracked_aggregates:
            all_events.extend(aggregate.domain_events)

        # Publish all events
        for event in all_events:
            event_bus.publish(event)

        # Clear events from aggregates after publishing
        for aggregate in self._tracked_aggregates:
            aggregate.clear_domain_events()

    def _get_repository(self, repo: type[R]) -> R:
        if repo not in self._repositories:
            from shared.infrastructure.ioc import get_injector

            injector = get_injector()
            try:
                repository = injector.get(repo)
                self._repositories[repo] = repository
            except Exception:
                raise ApplicationConfigurationError(
                    message=f"No repository registered for {repo}"
                )

        # Always set the unit of work reference so repositories can track aggregates
        # This ensures the reference is updated even for cached repositories
        repository = self._repositories[repo]
        if isinstance(repository, DjangoRepository):
            repository.set_unit_of_work(self)

        return repository

    def __getitem__(self, repo_type: type[R]) -> R:
        return self._get_repository(repo_type)
