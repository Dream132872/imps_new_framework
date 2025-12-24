"""
Attachment Command Handlers for CQRS implementations.
Handlers execute business logic for commands.
"""

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.commands import (
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.application.dtos import AttachmentDTO
from media.application.mappers import AttachmentDTOMapper
from media.domain.entities import Attachment
from media.domain.exceptions import AttachmentNotFoundError, AttachmentValidationError
from media.domain.repositories import AttachmentRepository
from media.infrastructure.services import FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.exceptions import DomainEntityNotFoundError
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


class CreateAttachmentCommandHandler(
    CommandHandler[CreateAttachmentCommand, AttachmentDTO],
    BaseAttachmentCommandHandler,
):
    def handle(self, command: CreateAttachmentCommand) -> AttachmentDTO:
        file_path = ""
        try:
            with self.uow:
                # save file using file_storage_service
                file_name = self.file_storage_service.save_file(command.file)

                if not file_name:
                    raise AttachmentValidationError(_("Invalid file"))

                # create attachment entity
                file_field = FileFieldFactory.from_file_name(file_name)
                file_path = file_field.path
                attachment = Attachment(
                    file=file_field,
                    content_type_id=command.content_type_id,
                    object_id=str(command.object_id),
                    attachment_type=command.attachment_type,
                    title=command.title,
                )

                # save attachment in db
                attachment = self.uow[AttachmentRepository].save(attachment)
                return AttachmentDTOMapper.to_dto(attachment)
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
                attachment = self.uow[AttachmentRepository].get_by_id(
                    str(command.attachment_id)
                )

                # old file name
                old_file_path = None

                # save new file for attachment
                if command.file:
                    # save old file path
                    old_file_path = attachment.file.path
                    # save new file in storage
                    new_file_name = self.file_storage_service.save_file(command.file)
                    # add saved file name to the attachment
                    attachment.update_file(
                        FileFieldFactory.from_file_name(new_file_name)
                    )

                # update attachment information
                attachment.update_information(
                    title=command.title, attachment_type=command.attachment_type
                )

                # save the new
                attachment = self.uow[AttachmentRepository].save(attachment)
                # remove previous file from storage at last step to avoid any errors
                if old_file_path:
                    self.file_storage_service.delete_file(old_file_path)

                return AttachmentDTOMapper.to_dto(attachment)
        except AttachmentNotFoundError as e:
            raise map_domain_exception_to_application(
                e, _("Attachment not found: {msg}").format(msg=str(e))
            ) from e
        except AttachmentValidationError as e:
            raise map_domain_exception_to_application(
                e, _("Invalid attachment: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("An error occurred during updating attachment: {msg}").format(
                    msg=str(e)
                )
            ) from e


class DeleteAttachmentCommandHandler(
    CommandHandler[DeleteAttachmentCommand, AttachmentDTO],
    BaseAttachmentCommandHandler,
):
    def handle(self, command: DeleteAttachmentCommand) -> AttachmentDTO:
        try:
            with self.uow:
                # get attachment by it's id
                attachment = self.uow[AttachmentRepository].get_by_id(str(command.pk))
                # delete attachment from db
                self.uow[AttachmentRepository].delete(attachment)
                # remove file from storage
                self.file_storage_service.delete_file(attachment.file.path)
                return AttachmentDTOMapper.to_dto(attachment)
        except AttachmentNotFoundError as e:
            # Use the exception mapper for automatic transformation
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            # Handle unexpected exceptions
            raise ApplicationError(
                _(
                    "Failed to delete attachment with ID '{attachment_id}': {message}"
                ).format(attachment_id=command.pk, message=str(e)),
                details={"attachment_id": command.pk},
            ) from e
