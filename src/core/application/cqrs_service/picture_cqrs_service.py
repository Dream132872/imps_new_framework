"""
CQRS Service for Picture.
"""

from core.application.command_handlers import picture_command_handlers
from core.application.commands import picture_commands
from core.application.queries import picture_queries
from core.application.query_handlers import picture_query_handlers
from shared.application.cqrs import register_command_handler, register_query_handler

# ============================
# register queries
# ============================
register_query_handler(
    picture_queries.GetPictureByIdQuery,
    picture_query_handlers.GetPictureByIdQueryHandler,
)
register_query_handler(
    picture_queries.SearchPicturesQuery,
    picture_query_handlers.SearchPicturesQueryHandler,
)
register_query_handler(
    picture_queries.SearchFirstPictureQuery,
    picture_query_handlers.SearchFirstPictureQueryHandler,
)

# ============================
# register commands
# ============================
register_command_handler(
    picture_commands.CreatePictureCommand,
    picture_command_handlers.CreatePictureCommandHandler,
)
register_command_handler(
    picture_commands.UpdatePictureCommand,
    picture_command_handlers.UpdatePictureCommandHandler,
)
register_command_handler(
    picture_commands.DeletePictureCommand,
    picture_command_handlers.DeletePictureCommandHandler,
)
