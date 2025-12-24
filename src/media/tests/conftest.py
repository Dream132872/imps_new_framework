"""
Media related fixtures.
"""

import uuid
from typing import Callable
from unittest.mock import MagicMock

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.entities.chunk_upload_entities import ChunkUpload as ChunkUploadEntity
from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.domain.entities.picture_entities import Picture as PictureEntity
from media.domain.repositories import (
    AttachmentRepository,
    ChunkUploadRepository,
    PictureRepository,
)
from media.infrastructure.services import FileStorageService
from media.infrastructure.models import Picture as PictureModel
from shared.domain.entities import FileField, FileFieldType
from shared.infrastructure.ioc import UnitOfWork


@pytest.fixture
def image_file_factory() -> Callable[..., SimpleUploadedFile]:
    """Created a factory for SimpleUploadedFile"""

    def _create_factory(**kwargs) -> SimpleUploadedFile:  # type: ignore
        return SimpleUploadedFile(
            name=kwargs.get("name", "test_image.jpg"),
            content=kwargs.get("content", b"fake image content"),
            content_type=kwargs.get("content_type", "images/jpeg"),
        )

    return _create_factory


@pytest.fixture
def sample_image_file(
    image_file_factory: Callable[..., SimpleUploadedFile],
) -> SimpleUploadedFile:
    """Creating a sample image file for testing."""

    return image_file_factory()


@pytest.fixture
def image_file_field_factory(db: None) -> Callable[..., FileField]:
    """Image file field factory."""

    def _create_file_field(**kwargs) -> FileField:  # type: ignore
        return FileField(
            file_type=FileFieldType.IMAGE,
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
) -> Callable[..., PictureEntity]:
    """Picture entity factory."""

    def _create_picture_entity(**kwargs) -> PictureEntity:  # type: ignore
        return PictureEntity(
            id=kwargs.get("picture_id", None),
            image=kwargs.get("image", sample_image_file_field),
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
            file_type=FileFieldType.FILE,
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
    """Factory of attachment entity"""

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
    """Creates a sample of chunk upload entity"""

    return chunk_upload_entity_factory()


@pytest.fixture
def mock_picture_repository() -> MagicMock:
    """Creates a MagicMock object of picture repository"""

    return MagicMock(spec=PictureRepository)


@pytest.fixture
def mock_attachment_repository() -> MagicMock:
    """Creates a MagicMock object of attachment repository"""

    return MagicMock(spec=AttachmentRepository)


@pytest.fixture
def mock_chunk_upload_repository() -> MagicMock:
    """Creates a MagicMock object from chunk upload repository"""

    return MagicMock(spec=ChunkUploadRepository)


@pytest.fixture
def mock_unit_of_work(
    mock_picture_repository: MagicMock,
    mock_attachment_repository: MagicMock,
    mock_chunk_upload_repository: MagicMock,
) -> MagicMock:
    """Created a MagicMock object of unit of work"""

    mock_uow = MagicMock(spec=UnitOfWork)

    mock_uow.__get_item__ = MagicMock(
        side_effect=lambda key: {
            PictureRepository: mock_picture_repository,
            AttachmentRepository: mock_attachment_repository,
            ChunkUploadRepository: mock_chunk_upload_repository,
        }.get(key)
    )

    mock_uow.__enter__.return_value = mock_uow

    return mock_uow


@pytest.fixture
def mock_file_storage_service() -> MagicMock:
    """Created MagicMock object of file storage service"""

    return MagicMock(spec=FileStorageService)
