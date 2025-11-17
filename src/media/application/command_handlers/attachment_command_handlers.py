"""
Attachment Command Handlers for CQRS implementations.
Handlers execute business logic for commands.
"""

from typing import Any

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.commands import (
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.application.dtos import AttachmentDTO
from media.domain.entities import Attachment
from media.domain.exceptions import AttachmentNotFoundError, AttachmentValidationError
from media.domain.repositories import AttachmentRepository
from media.domain.services import FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.dtos import FileFieldDTO
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.factories import FileFieldFactory
from shared.domain.repositories import UnitOfWork


class BaseAttachmentCommandHandler:
    @inject
    def __init__(
        self,
        uow: UnitOfWork,
        file_storage_service: FileStorageService,
    ) -> None:
        self.uow = uow
        self.file_storage_service = file_storage_service

    def _to_dto(self, attachment: Attachment) -> AttachmentDTO:
        file = FileFieldDTO(
            file_type="file",
            url=attachment.file.url,
            name=attachment.file.name,
            size=attachment.file.size,
            width=None,
            height=None,
            content_type=attachment.file.content_type,
        )
        return AttachmentDTO(
            id=attachment.id,
            file=file,
            title=attachment.title,
            content_type=attachment.content_type,
            object_id=attachment.object_id,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )


class CreateAttachmentCommandHandler(
    CommandHandler[CreateAttachmentCommand, AttachmentDTO],
    BaseAttachmentCommandHandler,
):
    def handle(self, command: CreateAttachmentCommand) -> AttachmentDTO:
        file_path = ""
        try:
            # check the file is not empty
            if not command.file:
                raise AttachmentValidationError(_("You should pass the file"))

            with self.uow:
                # save file using file_storage_service
                file_name = self.file_storage_service.save_file(command.file)

                # create attachment entity
                file_field = FileFieldFactory.from_file_name(file_name)
                file_path = file_field.path
                attachment = Attachment(
                    file=file_field,
                    content_type_id=command.content_type_id,
                    object_id=command.object_id,
                    title=command.title,
                )

                # save attachment in db
                attachment = self.uow[AttachmentRepository].save(attachment)
                return self._to_dto(attachment)
        except AttachmentValidationError as e:
            self.file_storage_service.delete_file(file_path)
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            self.file_storage_service.delete_file(file_path)
            raise ApplicationError(
                _("Failed to create attachment: {message}").format(message=str(e))
            ) from e


class UpdateAttachmentCommandHandler(
    CommandHandler[UpdateAttachmentCommand, AttachmentDTO],
    BaseAttachmentCommandHandler,
):
    def handle(self, command: UpdateAttachmentCommand) -> AttachmentDTO:
        try:
            with self.uow:
                # get attachment by it's id
                attachment = self.uow[AttachmentRepository].get_by_id(str(command.attachment_id))
                # raise not found error if the attachment does not exist
                if not attachment:
                    raise AttachmentNotFoundError(
                        _("There is no attachment with ID: {attachment_id}").format(
                            attachment_id=command.attachment_id
                        )
                    )

                # save new file for attachment
                if command.file:
                    # save new file in storage
                    new_file_name = self.file_storage_service.save_file(command.file)
                    # remove previous file from storage
                    self.file_storage_service.delete_file(attachment.file.name)
                    # add saved file name to the attachment
                    attachment.update_file(
                        FileFieldFactory.from_file_name(new_file_name)
                    )

                # update attachment information
                attachment.update_information(
                    title=command.title
                )

                # save the new
                attachment = self.uow[AttachmentRepository].save(attachment)
                return self._to_dto(attachment)
        except AttachmentNotFoundError as e:
            raise map_domain_exception_to_application(
                e, _("Attachment not found: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("An error occurred during updating attachment: {msg}").format(msg=str(e))
            ) from e


class DeleteAttachmentCommandHandler(
    CommandHandler[DeleteAttachmentCommand, AttachmentDTO],
    BaseAttachmentCommandHandler,
):
    def handle(self, command: DeleteAttachmentCommand) -> AttachmentDTO:
        try:
            attachment = self.uow[AttachmentRepository].get_by_id(str(command.pk))
            if not attachment:
                raise AttachmentNotFoundError(
                    _("Attachment with ID {attachment_id} not found").format(
                        attachment_id=command.pk
                    )
                )

            self.uow[AttachmentRepository].delete(attachment)
            self.file_storage_service.delete_file(attachment.file.path)
            return self._to_dto(attachment)
        except AttachmentNotFoundError as e:
            # Use the exception mapper for automatic transformation
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            # Handle unexpected exceptions
            raise ApplicationError(
                _("Failed to delete attachment with ID '{attachment_id}': {message}").format(
                    attachment_id=command.pk, message=str(e)
                ),
                details={"attachment_id": command.pk},
            ) from e

