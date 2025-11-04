"""
Picture Command Handlers for CQRS implementations.
Handlers execute business logic for commands.
"""

from django.utils.translation import gettext_lazy as _
from injector import inject

from core.application.commands import picture_commands
from core.domain.exceptions.picture import PictureNotFoundError
from core.domain.repositories import PictureRepository
from core.domain.services import FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.repositories import UnitOfWork


class BasePictureCommandHandler:
    @inject
    def __init__(
        self, uow: UnitOfWork, file_storage_service: FileStorageService
    ) -> None:
        self.uow = uow
        self.file_storage_service = file_storage_service


class DeletePictureCommandHandler(
    CommandHandler[picture_commands.DeletePictureCommand, str],
    BasePictureCommandHandler,
):
    def handle(self, command: picture_commands.DeletePictureCommand) -> str:
        try:
            picture = self.uow[PictureRepository].get_by_id(str(command.pk))
            if not picture:
                raise PictureNotFoundError(
                    _("Picture with ID {picture_id} not found").format(
                        picture_id=command.pk
                    )
                )

            # picture.add_domain_event()
            self.uow[PictureRepository].delete(picture)
            return str(command.pk)
        except PictureNotFoundError as e:
            # Use the exception mapper for automatic transformation
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            # Handle unexpected exceptions
            raise ApplicationError(
                _("Failed to delete picture with ID '{picture_id}': {message}").format(
                    picture_id=command.pk, message=str(e)
                ),
                details={"picture_id": command.pk},
            ) from e
