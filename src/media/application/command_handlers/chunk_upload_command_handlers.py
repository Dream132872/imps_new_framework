"""
Chunk Upload Command Handlers for CQRS implementations.
"""

import uuid
from typing import Any, BinaryIO

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application import commands as chunk_upload_commands
from media.domain.entities import ChunkUpload
from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.domain.exceptions import ChunkUploadNotFoundError, ChunkUploadValidationError
from media.domain.repositories import ChunkUploadRepository
from media.domain.services import ChunkUploadService, FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.repositories import UnitOfWork

__all__ = (
    "CreateChunkUploadCommandHandler",
    "UploadChunkCommandHandler",
    "CompleteChunkUploadCommandHandler",
)


class BaseChunkUploadCommandHandler:
    @inject
    def __init__(
        self,
        uow: UnitOfWork,
        file_storage_service: FileStorageService,
        chunk_upload_service: ChunkUploadService,
    ) -> None:
        if not chunk_upload_service:
            raise ApplicationError(_("Chunk upload service not available"))

        self.uow = uow
        self.file_storage_service = file_storage_service
        self.chunk_upload_service = chunk_upload_service


class CreateChunkUploadCommandHandler(
    CommandHandler[chunk_upload_commands.CreateChunkUploadCommand, dict[str, Any]],
    BaseChunkUploadCommandHandler,
):
    def handle(
        self, command: chunk_upload_commands.CreateChunkUploadCommand
    ) -> dict[str, Any]:
        try:
            chunk_upload = ChunkUpload(
                upload_id=uuid.uuid4(),
                filename=command.filename,
                total_size=command.total_size,
                status=ChunkUploadStatus.PENDING,
            )
            chunk_upload = self.uow[ChunkUploadRepository].save(chunk_upload)
            return {
                "upload_id": chunk_upload.upload_id,
                "offset": 0,
            }
        except ChunkUploadValidationError as e:
            raise map_domain_exception_to_application(e, str(e))
        except Exception as e:
            raise ApplicationError(
                _("Failed to create chunk upload: {message}").format(message=str(e))
            ) from e


class UploadChunkCommandHandler(
    CommandHandler[chunk_upload_commands.UploadChunkCommand, dict[str, Any]],
    BaseChunkUploadCommandHandler,
):
    def handle(
        self, command: chunk_upload_commands.UploadChunkCommand
    ) -> dict[str, Any]:
        try:
            uploaded_size = self.chunk_upload_service.append_chunk(
                command.upload_id,
                command.chunk,
                command.offset,
                command.chunk_size,
            )

            chunk_upload = self.uow[ChunkUploadRepository].get_by_upload_id(
                command.upload_id
            )

            return {
                "upload_id": command.upload_id,
                "offset": uploaded_size,
                "progress": chunk_upload.get_progress_percent(),
                "completed": chunk_upload.is_complete(),
            }
        except ValueError as e:
            raise ApplicationError(str(e)) from e
        except ChunkUploadNotFoundError as e:
            raise map_domain_exception_to_application(
                e,
                _("An error occurred while chunk uploading: {msg}").format(msg=str(e)),
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("Failed to upload chunk: {message}").format(message=str(e))
            ) from e


class CompleteChunkUploadCommandHandler(
    CommandHandler[chunk_upload_commands.CompleteChunkUploadCommand, BinaryIO],
    BaseChunkUploadCommandHandler,
):
    def handle(
        self, command: chunk_upload_commands.CompleteChunkUploadCommand
    ) -> BinaryIO:
        if not self.chunk_upload_service:
            raise ApplicationError(_("Chunk upload service not available"))

        try:
            chunk_upload = self.uow[ChunkUploadRepository].get_by_upload_id(
                command.upload_id
            )

            chunk_upload.complete()

            self.uow[ChunkUploadRepository].save(chunk_upload)

            completed_file = self.chunk_upload_service.get_completed_file(
                command.upload_id
            )
            self.chunk_upload_service.cleanup_upload(command.upload_id)
            return completed_file
        except ChunkUploadValidationError as e:
            raise map_domain_exception_to_application(e) from e
        except ValueError as e:
            raise ApplicationError(str(e)) from e
        except Exception as e:
            if self.chunk_upload_service:
                try:
                    self.chunk_upload_service.cleanup_upload(command.upload_id)
                except Exception:
                    pass
            raise ApplicationError(
                _("Failed to complete chunk upload: {message}").format(message=str(e))
            ) from e
