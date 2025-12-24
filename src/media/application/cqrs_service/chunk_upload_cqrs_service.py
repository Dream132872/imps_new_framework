"""
CQRS Service for Chunk Upload.
"""

from media.application.commands import (
    CompleteChunkUploadCommand,
    CreateChunkUploadCommand,
    UploadChunkCommand,
)
from media.application.command_handlers import (
    CompleteChunkUploadCommandHandler,
    CreateChunkUploadCommandHandler,
    UploadChunkCommandHandler,
)
from media.application.queries import GetChunkUploadStatusQuery
from media.application.query_handlers import GetChunkUploadStatusQueryHandler
from shared.application.cqrs import register_command_handler, register_query_handler

# ============================
# register queries
# ============================
register_query_handler(
    GetChunkUploadStatusQuery,
    GetChunkUploadStatusQueryHandler,
)

# ============================
# register commands
# ============================
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

