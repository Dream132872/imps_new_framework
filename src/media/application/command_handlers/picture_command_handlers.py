"""
Picture Command Handlers for CQRS implementations.
Handlers execute business logic for commands.
"""

from django.utils.translation import gettext_lazy as _
from injector import inject

from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from media.application.dtos import PictureDTO
from media.application.mappers import PictureDTOMapper
from media.domain.entities import Picture
from media.domain.exceptions import PictureNotFoundError, PictureValidationError
from media.domain.repositories import PictureRepository
from media.domain.services import FileStorageService
from shared.application.cqrs import CommandHandler
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.application.exceptions import ApplicationError
from shared.domain.factories import FileFieldFactory
from shared.domain.repositories import UnitOfWork


class BasePictureCommandHandler:
    @inject
    def __init__(
        self,
        uow: UnitOfWork,
        file_storage_service: FileStorageService,
    ) -> None:
        self.uow = uow
        self.file_storage_service = file_storage_service


class CreatePictureCommandHandler(
    CommandHandler[CreatePictureCommand, PictureDTO],
    BasePictureCommandHandler,
):
    def handle(self, command: CreatePictureCommand) -> PictureDTO:
        image_path = ""

        try:
            with self.uow:
                # save image using file_storage_service
                image_name = self.file_storage_service.save_image(command.image)

                if not image_name:
                    raise PictureValidationError(_("You should pass the image file"))

                # create picture entity
                image_file = FileFieldFactory.from_image_name(image_name)
                image_path = image_file.path
                picture = Picture(
                    image=image_file,
                    picture_type=command.picture_type,
                    content_type_id=command.content_type_id,
                    object_id=str(command.object_id),
                    title=command.title,
                    alternative=command.alternative,
                )

                # save picture in db
                picture = self.uow[PictureRepository].save(picture)
                return PictureDTOMapper.to_dto(picture)
        except PictureValidationError as e:
            self.file_storage_service.delete_image(image_path)
            raise map_domain_exception_to_application(e) from e
        except Exception as e:
            self.file_storage_service.delete_image(image_path)
            raise ApplicationError(
                _("Failed to create picture: {message}").format(message=str(e))
            ) from e


class UpdatePictureCommandHandler(
    CommandHandler[UpdatePictureCommand, PictureDTO],
    BasePictureCommandHandler,
):
    def handle(self, command: UpdatePictureCommand) -> PictureDTO:
        try:
            with self.uow:
                # get picture by it's id
                picture = self.uow[PictureRepository].get_by_id(str(command.picture_id))
                # old image path
                old_image_path = None

                # save new image for picture
                if command.image:
                    # save new image in storage
                    new_image_name = self.file_storage_service.save_image(command.image)
                    # old image path
                    old_image_path = picture.image.path
                    # add saved image name to the picture
                    picture.update_image(
                        FileFieldFactory.from_image_name(new_image_name)
                    )

                # update picture information
                picture.update_information(
                    title=command.title, alternative=command.alternative
                )

                # save the new
                picture = self.uow[PictureRepository].save(picture)
                # remove previouse image file from storage
                if old_image_path:
                    self.file_storage_service.delete_image(old_image_path)

                return PictureDTOMapper.to_dto(picture)
        except PictureNotFoundError as e:
            raise map_domain_exception_to_application(
                e, _("Picture not found: {msg}").format(msg=str(e))
            ) from e
        except PictureValidationError as e:
            raise map_domain_exception_to_application(
                e, _("Picture has validation error: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            raise ApplicationError(
                _("An error occurred during updating picture: {msg}").format(msg=str(e))
            ) from e


class DeletePictureCommandHandler(
    CommandHandler[DeletePictureCommand, PictureDTO],
    BasePictureCommandHandler,
):
    def handle(self, command: DeletePictureCommand) -> PictureDTO:
        try:
            with self.uow:
                # get picture by id
                picture = self.uow[PictureRepository].get_by_id(str(command.pk))
                # delete picture from db
                self.uow[PictureRepository].delete(picture)
                # remove image from storage
                self.file_storage_service.delete_image(picture.image.path)
                # return the deleted picture as a result
                return PictureDTOMapper.to_dto(picture)
        except PictureNotFoundError as e:
            # Use the exception mapper for automatic transformation
            raise map_domain_exception_to_application(
                e, message=_("Picture not found: {msg}").format(msg=str(e))
            ) from e
        except Exception as e:
            # Handle unexpected exceptions
            raise ApplicationError(
                _("Failed to delete picture with ID '{picture_id}': {message}").format(
                    picture_id=command.pk, message=str(e)
                ),
                details={"picture_id": command.pk},
            ) from e
