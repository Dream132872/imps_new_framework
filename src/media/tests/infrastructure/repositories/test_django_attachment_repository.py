import uuid
from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.domain.entities.attachment_entities import Attachment as AttachmentEntity
from media.domain.exceptions import AttachmentNotFoundError
from media.infrastructure.models import Attachment as AttachmentModel
from media.infrastructure.repositories import DjangoAttachmentRepository
from shared.domain.exceptions import DomainEntityNotFoundError
from shared.domain.factories import FileFieldFactory

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


def _stored_attachment_file_field(
    sample_attachment_file: SimpleUploadedFile, sample_content_type: ContentType
):
    """
    Create a FileField-backed file in storage, then convert it to the domain FileField.

    We delete the temp model to avoid leaving unrelated DB rows around; the file remains in storage.
    """
    temp_model = AttachmentModel.objects.create(
        file=sample_attachment_file,
        content_type=sample_content_type,
        object_id="temp-obj",
        attachment_type="temp",
    )
    file_field = FileFieldFactory.from_file_field(temp_model.file)
    temp_model.delete()
    return file_field


class TestDjangoAttachmentRepository:
    def test_get_by_id_returns_domain_entity(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        saved = repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                title="Doc",
                content_type_id=sample_content_type.id,
            )
        )

        retrieved = repo.get_by_id(saved.id)

        assert retrieved.id == saved.id
        assert retrieved.content_type_id == sample_content_type.id
        assert retrieved.object_id == "obj-1"
        assert retrieved.attachment_type == "document"
        assert retrieved.title == "Doc"
        assert retrieved.file.name.startswith("attachments/")

    def test_get_by_id_raises_not_found(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()
        repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                content_type_id=sample_content_type.id,
            )
        )

        with pytest.raises(AttachmentNotFoundError):
            repo.get_by_id(str(uuid.uuid4()))

    def test_save_updates_existing_entity(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        saved = repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                title="Original Title",
                content_type_id=sample_content_type.id,
            )
        )

        updated = repo.save(
            attachment_entity_factory(
                attachment_id=saved.id,
                file=file_field,
                object_id="obj-1",
                attachment_type="image",
                title="Updated Title",
                content_type_id=sample_content_type.id,
            )
        )

        assert updated.id == saved.id
        assert updated.attachment_type == "image"
        assert updated.title == "Updated Title"

    def test_delete_removes_entity(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        saved = repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                content_type_id=sample_content_type.id,
            )
        )

        repo.delete(saved)

        with pytest.raises(AttachmentNotFoundError):
            repo.get_by_id(saved.id)

    def test_delete_raises_not_found(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        entity = attachment_entity_factory(
            attachment_id=str(uuid.uuid4()),
            file=file_field,
            object_id="obj-1",
            attachment_type="document",
            content_type_id=sample_content_type.id,
        )

        with pytest.raises(DomainEntityNotFoundError):
            repo.delete(entity)

    def test_search_attachments_filters_and_orders_by_display_order(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        saved1 = repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                content_type_id=sample_content_type.id,
            )
        )
        saved2 = repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="DOCUMENT",  # case-insensitive match
                content_type_id=sample_content_type.id,
            )
        )
        repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-2",
                attachment_type="document",
                content_type_id=sample_content_type.id,
            )
        )

        AttachmentModel.objects.filter(id=saved1.id).update(display_order=2)
        AttachmentModel.objects.filter(id=saved2.id).update(display_order=1)

        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="document",
        )

        assert [r.id for r in results] == [saved2.id, saved1.id]

    def test_search_attachments_empty_type_disables_type_filter(
        self,
        sample_attachment_file: SimpleUploadedFile,
        sample_content_type: ContentType,
        attachment_entity_factory: Callable[..., AttachmentEntity],
    ) -> None:
        file_field = _stored_attachment_file_field(
            sample_attachment_file, sample_content_type
        )
        repo = DjangoAttachmentRepository()

        repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="document",
                content_type_id=sample_content_type.id,
            )
        )
        repo.save(
            attachment_entity_factory(
                file=file_field,
                object_id="obj-1",
                attachment_type="image",
                content_type_id=sample_content_type.id,
            )
        )

        results = repo.search_attachments(
            content_type=sample_content_type.id,
            object_id="obj-1",
            attachment_type="",
        )

        assert len(results) == 2

    def test_search_first_attachment_returns_none_when_no_matches(
        self,
        sample_content_type: ContentType,
    ) -> None:
        repo = DjangoAttachmentRepository()

        result = repo.search_first_attachment(
            content_type=sample_content_type.id,
            object_id="non-existent",
            attachment_type="document",
        )

        assert result is None

