"""
Implementation of pagination dto.
"""

from dataclasses import dataclass
from typing import Any

__all__ = ("PaginationInfoDTO", "PaginatedResultDTO")


@dataclass
class PaginationInfoDTO:
    """Information about pagination."""

    total_items_count: int
    page: int
    page_size: int
    total_pages: int
    has_previous: bool
    previous_page: int | None
    has_next: bool
    next_page: int | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items_count": self.total_items_count,
            "total_pages": self.total_pages,
            "has_previous": self.has_previous,
            "previous_page": self.previous_page,
            "has_next": self.has_next,
            "next_page": self.next_page,
        }


@dataclass
class PaginatedResultDTO:
    """Paginated result containing items and pagination info."""

    items: list[Any]
    pagination_info: PaginationInfoDTO

    @property
    def is_paginated(self) -> bool:
        """Check if the result is paginated."""
        return self.pagination_info.total_pages > 1
