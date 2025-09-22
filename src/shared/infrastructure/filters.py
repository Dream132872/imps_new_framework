"""
Base filters for infrastructure layer.
"""

from typing import Any
import django_filters


class BaseFilter(django_filters.FilterSet):
    class Meta:
        abstract = True

    def _to_query_params(self) -> dict[str, Any]:
        """Convert filter data to query parameters for application layer."""

        return (
            {key: value for key, value in self.data.items() if self.value}
            if self.data
            else {}
        )
