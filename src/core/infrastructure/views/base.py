import logging
from typing import Any, Hashable

from core.domain.repositories import UserRepository
from shared.domain.repositories import UnitOfWork
from shared.infrastructure.ioc import inject_dependencies
from shared.infrastructure.views import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/admin/home.html"

    @inject_dependencies()
    def __init__(self, uow: UnitOfWork, **kwargs: dict[Hashable, Any]) -> None:
        self.uow: UnitOfWork = uow
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        with self.uow:
            print(
                self.uow[UserRepository].get_by_id(
                    "2b8b8212-ef3f-4eb5-9893-c29675297087"
                )
            )
        return super().get_context_data(**kwargs)
