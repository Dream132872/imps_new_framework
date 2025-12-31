"""Integration tests for attachment views."""

import uuid
from typing import TYPE_CHECKING

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

if TYPE_CHECKING:
    from django.test import RequestFactory

from identity.infrastructure.models.user import User
from media.application.dtos import AttachmentDTO
from media.infrastructure.forms import AttachmentUpsertForm
from media.infrastructure.models import Attachment as AttachmentModel
from media.application.commands import DeleteAttachmentCommand
from media.infrastructure.views import (
    CreateAttachmentView,
    DeleteAttachmentView,
    UpdateAttachmentView,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


# Fixtures are now in conftest.py
# Use sample_attachment_file_pdf from conftest for PDF files


@pytest.mark.integration
class TestCreateAttachmentViewIntegration:
    """Integration tests for CreateAttachmentView."""

    def test_create_attachment_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test creating an attachment through the view with real command handler."""
        # Arrange
        object_id = str(uuid.uuid4())

        request = request_factory.post(
            "/",
            data={
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "document",
                "title": "Test Attachment",
            },
        )
        request.FILES["file"] = sample_attachment_file_pdf
        request.user = authenticated_user_with_permissions

        view = CreateAttachmentView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": object_id,
            "attachment_type": "document",
        }

        # Create form with request data
        form = AttachmentUpsertForm(
            data={
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "document",
                "title": "Test Attachment",
            },
            files={"file": sample_attachment_file_pdf},
        )

        # Act
        assert form.is_valid(), f"Form errors: {form.errors}"
        response = view.form_valid(form)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is False
        assert "attachment" in data["details"]

        # Verify attachment was actually created in database
        attachment_data = data["details"]["attachment"]
        attachment_id = attachment_data["id"]
        attachment = AttachmentModel.objects.get(id=attachment_id)
        assert attachment.title == "Test Attachment"
        assert attachment.attachment_type == "document"
        assert attachment.object_id == object_id
        assert attachment.content_type_id == sample_content_type.id
        assert attachment.file.name.startswith("attachments/")

    def test_get_initial_sets_correct_values(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
    ):
        """Test that get_initial sets correct values from URL kwargs."""
        view = CreateAttachmentView()
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
        }

        initial = view.get_initial()

        assert initial["content_type"] == str(sample_content_type.id)
        assert initial["object_id"] == str(view.kwargs["object_id"])
        assert initial["attachment_type"] == "document"


@pytest.mark.integration
class TestUpdateAttachmentViewIntegration:
    """Integration tests for UpdateAttachmentView."""

    def test_update_attachment_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test updating an attachment through the view with real command handler."""
        # Arrange: Create an attachment first
        object_id = str(uuid.uuid4())

        original_attachment = AttachmentModel.objects.create(
            file=sample_attachment_file_pdf,
            content_type=sample_content_type,
            object_id=object_id,
            attachment_type="document",
            title="Original Title",
        )

        # Update with new file and data
        new_file = SimpleUploadedFile(
            "updated_file.pdf", b"updated content", content_type="application/pdf"
        )
        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": str(original_attachment.id)}

        form = AttachmentUpsertForm(
            data={
                "attachment_id": str(original_attachment.id),
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "archive",
                "title": "Updated Title",
            },
            files={"file": new_file},
        )

        # Act
        assert form.is_valid(), f"Form errors: {form.errors}"
        response = view.form_valid(form)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is True

        # Verify attachment was actually updated in database
        updated_attachment = AttachmentModel.objects.get(id=original_attachment.id)
        assert updated_attachment.title == "Updated Title"
        assert updated_attachment.attachment_type == "archive"
        assert updated_attachment.file.name != original_attachment.file.name

    def test_update_attachment_without_new_file(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test updating an attachment without providing a new file."""
        # Arrange: Create an attachment first
        object_id = str(uuid.uuid4())

        original_attachment = AttachmentModel.objects.create(
            file=sample_attachment_file_pdf,
            content_type=sample_content_type,
            object_id=object_id,
            attachment_type="document",
            title="Original Title",
        )

        original_file_name = original_attachment.file.name

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": str(original_attachment.id)}

        form = AttachmentUpsertForm(
            data={
                "attachment_id": str(original_attachment.id),
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "document",
                "title": "Updated Title",
            },
        )

        # Act
        assert form.is_valid(), f"Form errors: {form.errors}"
        response = view.form_valid(form)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"

        # Verify attachment was updated but file remained the same
        updated_attachment = AttachmentModel.objects.get(id=original_attachment.id)
        assert updated_attachment.title == "Updated Title"
        assert updated_attachment.file.name == original_file_name

    def test_get_initial_loads_attachment_data(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test that get_initial loads attachment data from query."""
        # Arrange: Create an attachment
        attachment = AttachmentModel.objects.create(
            file=sample_attachment_file_pdf,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            attachment_type="document",
            title="Test Title",
        )

        view = UpdateAttachmentView()
        view.kwargs = {"attachment_id": str(attachment.id)}

        # Act
        initial = view.get_initial()

        # Assert
        assert initial["attachment_id"] == str(attachment.id)
        assert initial["content_type"] == attachment.content_type_id
        assert initial["object_id"] == attachment.object_id
        assert initial["attachment_type"] == attachment.attachment_type
        assert initial["title"] == attachment.title

    def test_get_form_sets_attachment_data(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test that get_form sets attachment_data on form."""
        # Arrange: Create an attachment
        attachment = AttachmentModel.objects.create(
            file=sample_attachment_file_pdf,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            attachment_type="document",
            title="Test Title",
        )

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": str(attachment.id)}

        # Act
        form = view.get_form()

        # Assert
        assert hasattr(form, "attachment_data")
        attachment_dto = form.attachment_data
        assert isinstance(attachment_dto, AttachmentDTO)
        assert str(attachment_dto.id) == str(attachment.id)
        assert attachment_dto.title == attachment.title


@pytest.mark.integration
class TestDeleteAttachmentViewIntegration:
    """Integration tests for DeleteAttachmentView."""

    def test_delete_attachment_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file_pdf: SimpleUploadedFile,
    ):
        """Test deleting an attachment through the view with real command handler."""
        # Arrange: Create an attachment
        attachment = AttachmentModel.objects.create(
            file=sample_attachment_file_pdf,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            attachment_type="document",
            title="Test Attachment",
        )

        attachment_id = attachment.id

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = DeleteAttachmentView()
        view.request = request
        view.command_class = DeleteAttachmentCommand

        # Act
        response = view.post(request, pk=str(attachment_id))

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert "details" in data
        assert "message" in data

        # Verify attachment was actually deleted from database
        assert not AttachmentModel.objects.filter(id=attachment_id).exists()

