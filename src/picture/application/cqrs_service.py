"""
CQRS Service for Picture.
"""

from picture.application.command_handlers import (
    CreatePictureCommandHandler,
    DeletePictureCommandHandler,
    UpdatePictureCommandHandler,
)
from picture.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from picture.application.queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from picture.application.query_handlers import (
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

