"""
CQRS Service for Core.
register all command and query handlers with the buses.
"""

from shared.application.cqrs import register_query_handler

from .command_handlers import *
from .commands import *
from .queries import *
from .query_handlers import *

# register queries
register_query_handler(GetUserByIdQuery, GetUserByIdQueryHandler)

# register commands
