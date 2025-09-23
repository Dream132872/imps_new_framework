"""
Domain-specific pagination implementation.
"""

import math
from dataclasses import dataclass
from typing import Any, Generic, Iterator, TypeVar

from .entities import Entity

T = TypeVar("T", bound=Entity)

__all__ = (
    "PaginationInfo",
    "DomainPaginator",
)


@dataclass(frozen=True)
class PaginationInfo:
    """Value object representing pagination metadata."""

    current_page: int
    page_size: int
    total_count: int

    def __post_init__(self) -> None:
        """Validate pagination parameters."""
        if self.current_page < 1:
            raise ValueError("Current page must be >= 1")
        if self.page_size < 1:
            raise ValueError("Page size must be >= 1")
        if self.total_count < 0:
            raise ValueError("Total count must be >= 0")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.page_size == 0:
            return 0
        return math.ceil(self.total_count / self.page_size)

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.current_page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.current_page > 1

    @property
    def next_page(self) -> int | None:
        """Get next page number if available."""
        return self.current_page + 1 if self.has_next else None

    @property
    def previous_page(self) -> int | None:
        """Get previous page number if available."""
        return self.current_page - 1 if self.has_previous else None

    @property
    def start_index(self) -> int:
        """Get the 1-based start index of items on current page."""
        return (self.current_page - 1) * self.page_size + 1

    @property
    def end_index(self) -> int:
        """Get the 1-based end index of items on current page."""
        return min(self.current_page * self.page_size, self.total_count)

    @property
    def is_empty(self) -> bool:
        """Check if there are no items to paginate."""
        return self.total_count == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "current_page": self.current_page,
            "page_size": self.page_size,
            "total_count": self.total_count,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
            "next_page": self.next_page,
            "previous_page": self.previous_page,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "is_empty": self.is_empty,
        }


class DomainPaginator(Generic[T]):
    """Domain-specific paginator that doesn't depend on Django."""

    def __init__(
        self,
        items: list[T],
        page: int = 1,
        page_size: int = 25,
        total_count: int | None = None,
    ):
        """
        Initialize paginator.

        Args:
            items: List of items for the current page
            page: Current page number (1-based)
            page_size: Number of items per page
            total_count: Total number of items across all pages
        """
        self._items = items
        self._page = page
        self._page_size = page_size
        self._total_count = total_count or len(items)

        # Create pagination info
        self._pagination_info = PaginationInfo(
            current_page=self._page,
            page_size=self._page_size,
            total_count=self._total_count,
        )

    @property
    def items(self) -> list[T]:
        """Get items for current page."""
        return self._items

    @property
    def pagination_info(self) -> PaginationInfo:
        """Get pagination metadata."""
        return self._pagination_info

    @property
    def current_page(self) -> int:
        """Get current page number."""
        return self._page

    @property
    def page_size(self) -> int:
        """Get page size."""
        return self._page_size

    @property
    def total_count(self) -> int:
        """Get total count of items."""
        return self._total_count

    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        return self._pagination_info.total_pages

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self._pagination_info.has_next

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self._pagination_info.has_previous

    @property
    def is_empty(self) -> bool:
        """Check if paginator is empty."""
        return self._pagination_info.is_empty

    def __len__(self) -> int:
        """Get number of items on current page."""
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Iterate over items on current page."""
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        """Get item by index on current page."""
        return self._items[index]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "items": [item.to_dict() for item in self._items],
            "pagination": self._pagination_info.to_dict(),
        }
