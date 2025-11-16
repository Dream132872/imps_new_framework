"""
CQRS Service for Media bounded context.
"""

from media.application.command_handlers import (
    CreatePictureCommandHandler,
    DeletePictureCommandHandler,
    UpdatePictureCommandHandler,
    CreateChunkUploadCommandHandler,
    UploadChunkCommandHandler,
    CompleteChunkUploadCommandHandler,
)
from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
    CreateChunkUploadCommand,
    UploadChunkCommand,
    CompleteChunkUploadCommand,
)
from media.application.queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
    GetChunkUploadStatusQuery,
)
from media.application.query_handlers import (
    GetPictureByIdQueryHandler,
    SearchFirstPictureQueryHandler,
    SearchPicturesQueryHandler,
    GetChunkUploadStatusQueryHandler,
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
register_query_handler(
    GetChunkUploadStatusQuery,
    GetChunkUploadStatusQueryHandler,
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
register_command_handler(
    CreateChunkUploadCommand,
    CreateChunkUploadCommandHandler,
)
register_command_handler(
    UploadChunkCommand,
    UploadChunkCommandHandler,
)
register_command_handler(
    CompleteChunkUploadCommand,
    CompleteChunkUploadCommandHandler,
)

