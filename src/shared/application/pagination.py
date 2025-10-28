"""
Pagination tools for converting DomainPaginator and PaginatedResultDTO.
"""

import logging
from typing import Any

from django.utils.translation import gettext_lazy as _

from shared.application.dtos import PaginatedResultDTO, PaginationInfoDTO
from shared.domain.pagination import DomainPaginator

__all__ = ("convert_to_paginated_result_dto",)

logger = logging.getLogger(__file__)


def convert_to_paginated_result_dto(
    paginated_object: DomainPaginator, items: list[Any]
) -> PaginatedResultDTO:
    """Converts DomainPaginator instance to PaginatedResultDTO

    Args:
        paginated_object (DomainPaginator): DomainPaginator instance of an entity.
        items (list[Any]): list of converted entities to dtos.

    Returns:
        PaginatedResultDTO: PaginatedResultDTO instance.
    """

    try:
        return PaginatedResultDTO(
            items=items,
            pagination_info=PaginationInfoDTO(
                total_items_count=paginated_object.total_count,
                page=paginated_object.current_page,
                page_size=paginated_object.page_size,
                next_page=paginated_object.pagination_info.next_page,
                has_next=paginated_object.pagination_info.has_next,
                has_previous=paginated_object.pagination_info.has_previous,
                previous_page=paginated_object.pagination_info.previous_page,
                total_pages=paginated_object.total_pages,
            ),
        )
    except Exception as err:
        logger.error(
            _(
                "Failed to convert DomainPaginator instance to PaginatedResultDTO: {message}"
            ).format(message=str(err))
        )
        raise err
