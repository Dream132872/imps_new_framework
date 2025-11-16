"""
CQRS Service for Chunk Upload (moved from core bounded context).
"""

from chunk_upload.application import command_handlers as chunk_upload_command_handlers
from chunk_upload.application import commands as chunk_upload_commands
from chunk_upload.application import queries as chunk_upload_queries
from chunk_upload.application import query_handlers as chunk_upload_query_handlers
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


