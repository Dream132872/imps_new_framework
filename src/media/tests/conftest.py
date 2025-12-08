"""
Media related fixtures.
"""

import uuid
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.entities.chunk_upload_entities import ChunkUpload as ChunkUploadEntity
from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.domain.entities.picture_entities import Picture as PictureEntity
from media.infrastructure.models import Picture as PictureModel
from shared.domain.entities import FileField, FileType


@pytest.fixture
def sample_image_file() -> SimpleUploadedFile:
    """Creating a sample image file for testing."""

    image_file = b"fake image content"
    return SimpleUploadedFile(
        name="test_image.jpg", content=image_file, content_type="image/jpeg"
    )


@pytest.fixture
def image_file_field_factory(db: None):
    """Image file field factory."""

    def _create_file_field(**kwargs):  # type: ignore
        return FileField(
            file_type=FileType.IMAGE,
            name=kwargs.get("image_name", "test_image.jpg"),
            path=kwargs.get("image_path", "/media/test_image.jpg"),
            url=kwargs.get("image_url", "/media/test_image.jpg"),
            width=int(kwargs.get("image_width", 1000)),
            height=int(kwargs.get("image_height", 700)),
            size=int(kwargs.get("image_size", 1024)),
            content_type=kwargs.get("image_content_type", "images/jpeg"),
        )

    return _create_file_field


@pytest.fixture
def sample_image_file_field(
    image_file_field_factory: Callable[..., FileField],
) -> FileField:
    """Creating a sample FileField."""

    return image_file_field_factory()


@pytest.fixture
def picture_entity_factory(
    db: None, sample_image_file_field: FileField, sample_content_type: ContentType
):
    """Picture entity factory."""

    def _create_picture_entity(**kwargs):  # type: ignore
        return PictureEntity(
            id=kwargs.get("picture_id", None),
            image=sample_image_file_field,
            picture_type=kwargs.get("picture_type", "main"),
            content_type_id=sample_content_type.id,
            object_id=kwargs.get("picture_object_id", str(uuid.uuid4())),
            title=kwargs.get("picture_title", "Image title"),
            alternative=kwargs.get("picture_alternative", "Image alternative"),
        )

    return _create_picture_entity


@pytest.fixture
def sample_picture_entity(
    db: None, picture_entity_factory: Callable[..., PictureEntity]
) -> PictureEntity:
    """Create a sample picture domain entity."""

    return picture_entity_factory()


@pytest.fixture
def sample_picture_model(
    sample_image_file: SimpleUploadedFile, sample_content_type: ContentType, db: None
) -> PictureModel:
    """
    Create a sample picture model.

    Returns a Picture instance with:
    - image: sample file field.
    - picture_type: main value ('main').
    - title: static title ('title').
    - alternative: static alternative ('alternative').
    """

    return PictureModel(
        image=sample_image_file,
        alternative="alternative",
        title="title",
        content_type=sample_content_type,
        object_id=str(uuid.uuid4()),
        picture_type="main",
        display_order=1,
    )


@pytest.fixture
def sample_attachment_file() -> SimpleUploadedFile:
    """Creating a sample file file for testing."""

    image_file = b"fake file content"

    return SimpleUploadedFile(
        name="test_file.rar",
        content=image_file,
        content_type="application/x-rar-compressed",
    )


@pytest.fixture
def attachment_file_field_factory(db: None) -> Callable[..., FileField]:
    """Attachment file field factory."""

    def _create_file_field(**kwargs):  # type: ignore
        return FileField(
            file_type=FileType.FILE,
            name=kwargs.get("file_name", "test_file.rar"),
            path=kwargs.get("file_path", "/media/test_file.rar"),
            url=kwargs.get("file_url", "/media/test_file.rar"),
            size=int(kwargs.get("file_size", 1024)),
            content_type=kwargs.get(
                "file_content_type", "application/x-rar-compressed"
            ),
        )

    return _create_file_field


@pytest.fixture
def sample_attachment_file_field(
    attachment_file_field_factory: Callable[..., FileField],
) -> FileField:
    """Creating a sample Attachment FileField."""

    return attachment_file_field_factory()


@pytest.fixture
def attachment_entity_factory(
    sample_content_type: ContentType, sample_attachment_file_field: FileField
) -> Callable[..., AttachmentEntity]:
    def _create_attachment(**kwargs) -> AttachmentEntity:  # type: ignore
        return AttachmentEntity(
            id=kwargs.get("attachment_id", None),
            file=kwargs.get("file", sample_attachment_file_field),
            attachment_type=kwargs.get("attachment_type", "document"),
            content_type_id=kwargs.get("content_type_id", sample_content_type.id),
            object_id=kwargs.get("object_id", str(uuid.uuid4())),
            title=kwargs.get("title", ""),
        )

    return _create_attachment


@pytest.fixture
def sample_attachment_entity(
    attachment_entity_factory: Callable[..., AttachmentEntity],
) -> AttachmentEntity:
    """Creates a sample of AttachmentEntity"""

    return attachment_entity_factory(title="Title of the attachment")


@pytest.fixture
def chunk_upload_entity_factory() -> Callable[..., ChunkUploadEntity]:
    """Creates chunk upload entity with desigred fields"""

    def _create_chunk_upload(**kwargs) -> ChunkUploadEntity:  # type: ignore
        return ChunkUploadEntity(
            id=kwargs.get("id", None),
            upload_id=kwargs.get("upload_id", str(uuid.uuid4())),
            filename=kwargs.get("filename", str(uuid.uuid4()) + ".rar"),
            total_size=kwargs.get("total_size", 2048),
            uploaded_size=kwargs.get("uploaded_size", 0),
            chunk_count=kwargs.get("chunk_count", 0),
            temp_file_path=kwargs.get("temp_file_path", None),
            status=kwargs.get("status", ChunkUploadStatus.PENDING),
        )

    return _create_chunk_upload


@pytest.fixture
def sample_chunk_upload_entity(
    chunk_upload_entity_factory: Callable[..., ChunkUploadEntity],
) -> ChunkUploadEntity:
    return chunk_upload_entity_factory()
