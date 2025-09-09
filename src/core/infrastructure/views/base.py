import logging
from typing import Any, Hashable

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
