import uuid
from io import BytesIO
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.exceptions import PictureNotFoundError
from media.infrastructure.models import Picture as PictureModel
from media.infrastructure.repositories import DjangoPictureRepository
from shared.domain.exceptions import DomainEntityNotFoundError
from shared.domain.factories import FileFieldFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


def _create_image_file(name: str = "test.png") -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(
        name=name, content=buffer.read(), content_type="image/png"
    )


def _stored_image_file_field(sample_content_type: ContentType):
    """
    Create an ImageField-backed file in storage, then convert it to the domain FileField.

    We delete the temp model to avoid leaving unrelated DB rows around; the file remains in storage.
    """
    temp_model = PictureModel.objects.create(
        image=_create_image_file(),
        content_type=sample_content_type,
        object_id="temp-obj",
        picture_type="temp",
    )
    file_field = FileFieldFactory.from_image_field(temp_model.image)
    temp_model.delete()
    return file_field


class TestDjangoPictureRepository:
    def test_get_by_id_returns_domain_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)

        entity = picture_entity_factory(
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
            picture_title="Cover",
            picture_alternative="Alt",
        )

        repo = DjangoPictureRepository()
        saved = repo.save(entity)

        retrieved = repo.get_by_id(saved.id)

        assert retrieved.id == saved.id
        assert retrieved.content_type_id == sample_content_type.id
        assert retrieved.object_id == "obj-1"
        assert retrieved.picture_type == "main"
        assert retrieved.title == "Cover"
        assert retrieved.alternative == "Alt"
        assert retrieved.image.name.startswith("images/")

    def test_get_by_id_raises_not_found(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()
        repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="main",
            )
        )

        with pytest.raises(PictureNotFoundError):
            repo.get_by_id(str(uuid.uuid4()))

    def test_save_updates_existing_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()

        saved = repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="main",
                picture_title="Original Title",
                picture_alternative="Original Alt",
            )
        )

        updated = repo.save(
            picture_entity_factory(
                picture_id=saved.id,
                image=file_field,
                picture_object_id="obj-1",
                picture_type="gallery",
                picture_title="Updated Title",
                picture_alternative="Updated Alt",
            )
        )

        assert updated.id == saved.id
        assert updated.picture_type == "gallery"
        assert updated.title == "Updated Title"
        assert updated.alternative == "Updated Alt"

    def test_delete_removes_entity(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()
        saved = repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="main",
            )
        )

        repo.delete(saved)

        with pytest.raises(PictureNotFoundError):
            repo.get_by_id(saved.id)

    def test_delete_raises_not_found(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()

        entity = picture_entity_factory(
            picture_id=str(uuid.uuid4()),
            image=file_field,
            picture_object_id="obj-1",
            picture_type="main",
        )

        with pytest.raises(DomainEntityNotFoundError):
            repo.delete(entity)

    def test_search_pictures_filters_and_orders_by_display_order(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()

        saved1 = repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="main",
            )
        )
        saved2 = repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="MAIN",  # case-insensitive match
            )
        )
        repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-2",
                picture_type="main",
            )
        )

        PictureModel.objects.filter(id=saved1.id).update(display_order=2)
        PictureModel.objects.filter(id=saved2.id).update(display_order=1)

        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="main",
        )

        assert [r.id for r in results] == [saved2.id, saved1.id]

    def test_search_pictures_empty_type_disables_type_filter(
        self,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        file_field = _stored_image_file_field(sample_content_type)
        repo = DjangoPictureRepository()

        repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="main",
            )
        )
        repo.save(
            picture_entity_factory(
                image=file_field,
                picture_object_id="obj-1",
                picture_type="gallery",
            )
        )

        results = repo.search_pictures(
            content_type=sample_content_type.id,
            object_id="obj-1",
            picture_type="",
        )

        assert len(results) == 2

    def test_search_first_picture_returns_none_when_no_matches(
        self,
        sample_content_type: ContentType,
    ) -> None:
        repo = DjangoPictureRepository()

        result = repo.search_first_picture(
            content_type=sample_content_type.id,
            object_id="non-existent",
            picture_type="main",
        )

        assert result is None
