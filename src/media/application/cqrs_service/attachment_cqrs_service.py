"""
CQRS Service for Attachment.
"""

from media.application.commands import (
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.application.command_handlers import (
    CreateAttachmentCommandHandler,
    DeleteAttachmentCommandHandler,
    UpdateAttachmentCommandHandler,
)
from media.application.queries import (
    GetAttachmentByIdQuery,
    SearchAttachmentsQuery,
    SearchFirstAttachmentQuery,
)
from media.application.query_handlers import (
    GetAttachmentByIdQueryHandler,
    SearchAttachmentsQueryHandler,
    SearchFirstAttachmentQueryHandler,
)
from shared.application.cqrs import register_command_handler, register_query_handler

# ============================
# register queries
# ============================
register_query_handler(
    GetAttachmentByIdQuery,
    GetAttachmentByIdQueryHandler,
)
register_query_handler(
    SearchAttachmentsQuery,
    SearchAttachmentsQueryHandler,
)
register_query_handler(
    SearchFirstAttachmentQuery,
    SearchFirstAttachmentQueryHandler,
)

# ============================
# register commands
# ============================
register_command_handler(
    CreateAttachmentCommand,
    CreateAttachmentCommandHandler,
)
register_command_handler(
    UpdateAttachmentCommand,
    UpdateAttachmentCommandHandler,
)
register_command_handler(
    DeleteAttachmentCommand,
    DeleteAttachmentCommandHandler,
)

