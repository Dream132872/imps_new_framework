"""
Chunk Upload Command Handlers for CQRS implementations.
"""

import uuid
from typing import Any

from django.utils.translation import gettext_lazy as _
from injector import inject

from chunk_upload.application import commands as chunk_upload_commands
from chunk_upload.domain.entities import ChunkUpload
from chunk_upload.domain.exceptions import ChunkUploadNotFoundError
from chunk_upload.domain.repositories import ChunkUploadRepository
from chunk_upload.domain.services import ChunkUploadService
from core.domain.services import FileStorageService
from picture.application.dtos import PictureDTO
from picture.domain.entities import Picture
from picture.domain.exceptions import PictureNotFoundError, PictureValidationError
from picture.domain.repositories import PictureRepository
from shared.application.cqrs import CommandHandler
from shared.application.dtos import FileFieldDTO
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.factories import FileFieldFactory
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
        self.uow = uow
        self.file_storage_service = file_storage_service
        self.chunk_upload_service = chunk_upload_service

    def _to_dto(self, picture: Picture) -> PictureDTO:
        image = FileFieldDTO(
            file_type="image",
            url=picture.image.url,
            name=picture.image.name,
            size=picture.image.size,
            width=picture.image.width,
            height=picture.image.height,
            content_type=picture.image.content_type,
        )
        return PictureDTO(
            id=picture.id,
            image=image,
            picture_type=picture.picture_type,
            title=picture.title,
            alternative=picture.alternative,
            content_type=picture.content_type,
            object_id=picture.object_id,
            created_at=picture.created_at,
            updated_at=picture.updated_at,
        )


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
                status="pending",
            )
            chunk_upload = self.uow[ChunkUploadRepository].save(chunk_upload)
            return {
                "upload_id": chunk_upload.upload_id,
                "offset": 0,
            }
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
        if not self.chunk_upload_service:
            raise ApplicationError(_("Chunk upload service not available"))

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
            if not chunk_upload:
                raise ChunkUploadNotFoundError(_("Chunk upload not found"))

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
    CommandHandler[chunk_upload_commands.CompleteChunkUploadCommand, PictureDTO],
    BaseChunkUploadCommandHandler,
):
    def handle(
        self, command: chunk_upload_commands.CompleteChunkUploadCommand
    ) -> PictureDTO:
        if not self.chunk_upload_service:
            raise ApplicationError(_("Chunk upload service not available"))

        image_path = ""
        try:
            chunk_upload = self.uow[ChunkUploadRepository].get_by_upload_id(
                command.upload_id
            )
            if not chunk_upload:
                raise ApplicationError(_("Chunk upload not found"))

            if not chunk_upload.is_complete():
                raise PictureValidationError(_("Upload is not completed yet"))

            with self.uow:
                if not self.uow[PictureRepository].is_valid_picture_type(
                    command.picture_type
                ):
                    raise PictureValidationError(_("Picture type is not valid"))

                completed_file = self.chunk_upload_service.get_completed_file(
                    command.upload_id
                )
                image_name = self.file_storage_service.save_image(completed_file)
                image_file = FileFieldFactory.from_image_name(image_name)
                image_path = image_file.path

                if command.picture_id:
                    picture = self.uow[PictureRepository].get_by_id(
                        str(command.picture_id)
                    )
                    if not picture:
                        raise PictureNotFoundError(
                            _("There is no picture with ID: {picture_id}").format(
                                picture_id=command.picture_id
                            )
                        )
                    self.file_storage_service.delete_image(picture.image.name)
                    picture.update_image(image_file)
                    picture.update_information(
                        title=command.title, alternative=command.alternative
                    )
                else:
                    picture = Picture(
                        image=image_file,
                        picture_type=command.picture_type,
                        content_type_id=command.content_type_id,
                        object_id=command.object_id,
                        title=command.title,
                        alternative=command.alternative,
                    )

                picture = self.uow[PictureRepository].save(picture)
                self.chunk_upload_service.cleanup_upload(command.upload_id)
                return self._to_dto(picture)
        except PictureValidationError as e:
            if image_path:
                self.file_storage_service.delete_image(image_path)
            raise map_domain_exception_to_application(e) from e
        except PictureNotFoundError as e:
            if image_path:
                self.file_storage_service.delete_image(image_path)
            raise map_domain_exception_to_application(e) from e
        except ValueError as e:
            if image_path:
                self.file_storage_service.delete_image(image_path)
            raise ApplicationError(str(e)) from e
        except Exception as e:
            if image_path:
                self.file_storage_service.delete_image(image_path)
            if self.chunk_upload_service:
                try:
                    self.chunk_upload_service.cleanup_upload(command.upload_id)
                except Exception:
                    pass
            raise ApplicationError(
                _("Failed to complete chunk upload: {message}").format(message=str(e))
            ) from e
