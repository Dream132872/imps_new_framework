"""
CQRS Service for Picture.
"""

from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from media.application.command_handlers import (
    CreatePictureCommandHandler,
    DeletePictureCommandHandler,
    UpdatePictureCommandHandler,
)
from media.application.queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from media.application.query_handlers import (
    GetPictureByIdQueryHandler,
    SearchFirstPictureQueryHandler,
    SearchPicturesQueryHandler,
)
from shared.application.cqrs import register_command_handler, register_query_handler

# ============================
# register queries
# ============================
register_query_handler(
    GetPictureByIdQuery,
    GetPictureByIdQueryHandler,
)
register_query_handler(
    SearchPicturesQuery,
    SearchPicturesQueryHandler,
)
register_query_handler(
    SearchFirstPictureQuery,
    SearchFirstPictureQueryHandler,
)

# ============================
# register commands
# ============================
register_command_handler(
    CreatePictureCommand,
    CreatePictureCommandHandler,
)
register_command_handler(
    UpdatePictureCommand,
    UpdatePictureCommandHandler,
)
register_command_handler(
    DeletePictureCommand,
    DeletePictureCommandHandler,
)

