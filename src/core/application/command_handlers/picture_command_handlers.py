"""
Picture Command Handlers for CQRS implementations.
Handlers execute business logic for commands.
"""

from django.utils.translation import gettext_lazy as _
from injector import inject

from core.application.commands import picture_commands
from core.application.dtos.picture_dtos import PictureDTO
from core.domain.entities.picture import Picture
from core.domain.exceptions.picture import PictureNotFoundError, PictureValidationError
from core.domain.repositories import PictureRepository
from core.domain.services import FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.dtos import FileFieldDTO
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError, ApplicationValidationError
from shared.domain.factories import FileFieldFactory
from shared.domain.repositories import UnitOfWork


class BasePictureCommandHandler:
    @inject
    def __init__(
        self, uow: UnitOfWork, file_storage_service: FileStorageService
    ) -> None:
        self.uow = uow
        self.file_storage_service = file_storage_service

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


class CreatePictureCommandHandler(
    CommandHandler[picture_commands.CreatePictureCommand, PictureDTO],
    BasePictureCommandHandler,
):
    def handle(self, command: picture_commands.CreatePictureCommand) -> PictureDTO:
        image_path = ""
        try:
            # raise PictureValidationError("Test error")
            # check the file is not empty
            if not command.image:
                raise PictureValidationError(_("You should pass the image file"))

            with self.uow:
                # check the type of picture is valid or not
                if not self.uow[PictureRepository].is_valid_picture_type(
                    command.picture_type
                ):
                    raise PictureValidationError(_("Picture type is not valid"))

                # save image using file_storage_service
                image_name = self.file_storage_service.save_image(command.image)

                # create picture entity
                image_file = FileFieldFactory.from_image_name(image_name)
                image_path = image_file.path
                picture = Picture(
                    image=image_file,
                    picture_type=command.picture_type,
                    content_type_id=command.content_type_id,
                    object_id=command.object_id,
                    title=command.title,
                    alternative=command.alternative,
                )

                # save picture in db
                picture = self.uow[PictureRepository].save(picture)
                return self._to_dto(picture)
        except PictureValidationError as e:
            self.file_storage_service.delete_image(image_path)
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            self.file_storage_service.delete_image(image_path)
            raise ApplicationError(
                _("Failed to create picture: {message}").format(message=str(e))
            ) from e


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
