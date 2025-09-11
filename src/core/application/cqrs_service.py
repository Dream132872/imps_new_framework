"""
CQRS Service for Core.
register all command and query handlers with the buses.
"""

from injector import inject

from shared.application.cqrs import register_command_handler, register_query_handler
from shared.domain.repositories import UnitOfWork

from .command_handlers import *
from .commands import *
from .queries import *
from .query_handlers import *


class CoreCQRSService:
    @inject
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self._register_all_handlers()

    def _register_all_handlers(self) -> None:
        register_query_handler(GetUserByIdQuery, GetProductByIdQueryHandler(self.uow))
