"""
Pagination tools for converting DomainPaginator and PaginatedResultDTO.
"""

from typing import Any

from shared.application.dtos import *
from shared.domain.pagination import *

__all__ = ("convert_to_paginated_result_dto",)


def convert_to_paginated_result_dto(
    paginated_entity: DomainPaginator, items: list[Any]
) -> PaginatedResultDTO:
    """Converts DomainPaginator instance to PaginatedResultDTO

    Args:
        paginated_entity (DomainPaginator): DomainPaginator instance of an entity.
        items (list[Any]): list of converted entities to dtos.

    Returns:
        PaginatedResultDTO: PaginatedResultDTO instance.
    """

    return PaginatedResultDTO(
        items=items,
        pagination_info=PaginationInfoDTO(
            total_items_count=paginated_entity.total_count,
            page=paginated_entity.current_page,
            page_size=paginated_entity.page_size,
            next_page=paginated_entity.pagination_info.next_page,
            has_next=paginated_entity.pagination_info.has_next,
            has_previous=paginated_entity.pagination_info.has_previous,
            previous_page=paginated_entity.pagination_info.previous_page,
            total_pages=paginated_entity.total_pages,
        ),
    )
