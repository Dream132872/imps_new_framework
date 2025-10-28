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
from shared.application.exceptions import ValidationError
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
            picture = self.uow[PictureRepository].get_by_id(str(command.picture_id))
            if not picture:
                raise PictureNotFoundError(
                    _(
                        "Picture with ID {picture_id} not found".format(
                            picture_id=command.picture_id
                        )
                    )
                )

            self.uow[PictureRepository].delete(picture)
            return str(command.picture_id)
        except Exception as e:
            raise ValidationError(
                "Failed to delete picture with ID '{picture_id}': {message}".format(
                    picture_id=command.picture_id, message=str(e)
                )
            )
