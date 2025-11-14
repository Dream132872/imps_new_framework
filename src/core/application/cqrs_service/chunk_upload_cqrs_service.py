"""
CQRS Service for Chunk Upload.
"""

from core.application.command_handlers import chunk_upload_command_handlers
from core.application.commands import chunk_upload_commands
from core.application.queries import chunk_upload_queries
from core.application.query_handlers import chunk_upload_query_handlers
from shared.application.cqrs import register_command_handler, register_query_handler

# ============================
# register queries
# ============================
register_query_handler(
    chunk_upload_queries.GetChunkUploadStatusQuery,
    chunk_upload_query_handlers.GetChunkUploadStatusQueryHandler,
)

# ============================
# register commands
# ============================
register_command_handler(
    chunk_upload_commands.CreateChunkUploadCommand,
    chunk_upload_command_handlers.CreateChunkUploadCommandHandler,
)
register_command_handler(
    chunk_upload_commands.UploadChunkCommand,
    chunk_upload_command_handlers.UploadChunkCommandHandler,
)
register_command_handler(
    chunk_upload_commands.CompleteChunkUploadCommand,
    chunk_upload_command_handlers.CompleteChunkUploadCommandHandler,
)


