"""
CQRS Service for Core.
register all command and query handlers with the buses.
"""

from core.application.command_handlers import *
from core.application.commands import *
from core.application.queries import *
from core.application.query_handlers import *
from core.application.query_handlers.user_query_handlers import SearchUsersQueryHandler
from shared.application.cqrs import register_query_handler

# register queries
register_query_handler(GetUserByIdQuery, GetUserByIdQueryHandler)
register_query_handler(SearchUsersQuery, SearchUsersQueryHandler)
