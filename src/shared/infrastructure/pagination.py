"""
Django Paginator Factory for creating Domain Paginators.
"""

from typing import Any, Callable, TypeVar

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet

from shared.domain.entities import Entity
from shared.domain.pagination import DomainPaginator

T = TypeVar("T", bound=Entity)

__all__ = ("DjangoPaginatorFactory",)


class DjangoPaginatorFactory:
    """
    Factory to create DomainPaginator from Django Paginator.
    This encapsulates Django-specific pagination logic while maintaining
    clean domain boundaries.
    """

    @staticmethod
    def create_domain_paginator(
        queryset: QuerySet,
        page: int,
        page_size: int,
        entity_converter: Callable[[Any], T],
        allow_empty_first_page: bool = True,
    ) -> DomainPaginator[T]:
        """
        Create a DomainPaginator from a Django QuerySet.

        Args:
            queryset: Django QuerySet to paginate
            page: Page number (1-based)
            page_size: Number of items per page
            entity_converter: Function to convert model instances to domain entities
            allow_empty_first_page: Whether to allow empty first page

        Returns:
            DomainPaginator: Domain-specific paginator instance

        Raises:
            ValueError: If page or page_size are invalid
        """
        # Validate inputs
        if page < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")

        # Create Django Paginator
        paginator = Paginator(queryset, page_size)

        # Handle empty queryset
        if paginator.count == 0 and not allow_empty_first_page:
            raise ValueError("Empty queryset not allowed")

        try:
            # Get the requested page
            page_obj = paginator.get_page(page)
        except (EmptyPage, PageNotAnInteger):
            # Django's get_page handles invalid pages gracefully
            # but we want to be explicit about our domain behavior
            page_obj = paginator.get_page(1)

        # Convert models to domain entities
        entities = [entity_converter(item) for item in page_obj]

        # Create and return domain paginator
        return DomainPaginator(
            items=entities,
            page=page_obj.number,
            page_size=page_size,
            total_count=paginator.count,
        )

    @staticmethod
    def create_domain_paginator_with_filters(
        base_queryset: QuerySet,
        filters: dict[str, Any],
        page: int,
        page_size: int,
        entity_converter: Callable[[Any], T],
    ) -> DomainPaginator[T]:
        """
        Create a DomainPaginator with applied filters.

        Args:
            base_queryset: Base Django QuerySet
            filters: Dictionary of field filters to apply
            page: Page number (1-based)
            page_size: Number of items per page
            entity_converter: Function to convert model instances to domain entities

        Returns:
            DomainPaginator: Domain-specific paginator instance
        """
        # Apply filters
        filtered_queryset = base_queryset.filter(**filters)

        return DjangoPaginatorFactory.create_domain_paginator(
            queryset=filtered_queryset,
            page=page,
            page_size=page_size,
            entity_converter=entity_converter,
        )

    @staticmethod
    def create_domain_paginator_with_ordering(
        queryset: QuerySet,
        page: int,
        page_size: int,
        entity_converter: Callable[[Any], T],
        ordering: list[str] | None = None,
    ) -> DomainPaginator[T]:
        """
        Create a DomainPaginator with custom ordering.

        Args:
            queryset: Django QuerySet to paginate
            page: Page number (1-based)
            page_size: Number of items per page
            entity_converter: Function to convert model instances to domain entities
            ordering: List of fields to order by

        Returns:
            DomainPaginator: Domain-specific paginator instance
        """
        if ordering:
            queryset = queryset.order_by(*ordering)

        return DjangoPaginatorFactory.create_domain_paginator(
            queryset=queryset,
            page=page,
            page_size=page_size,
            entity_converter=entity_converter,
        )

    @staticmethod
    def create_domain_paginator_with_select_related(
        queryset: QuerySet,
        page: int,
        page_size: int,
        entity_converter: Callable[[Any], T],
        select_related: list[str] | None = None,
    ) -> DomainPaginator[T]:
        """
        Create a DomainPaginator with select_related optimization.

        Args:
            queryset: Django QuerySet to paginate
            page: Page number (1-based)
            page_size: Number of items per page
            entity_converter: Function to convert model instances to domain entities
            select_related: List of related fields to select

        Returns:
            DomainPaginator: Domain-specific paginator instance
        """
        if select_related:
            queryset = queryset.select_related(*select_related)

        return DjangoPaginatorFactory.create_domain_paginator(
            queryset=queryset,
            page=page,
            page_size=page_size,
            entity_converter=entity_converter,
        )

