"""Tests for attachment views."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from identity.infrastructure.models.user import User
from media.application.commands import (
    CreateAttachmentCommand,
    DeleteAttachmentCommand,
    UpdateAttachmentCommand,
)
from media.application.dtos import AttachmentDTO
from media.application.queries import GetAttachmentByIdQuery
from media.infrastructure.views import (
    CreateAttachmentView,
    DeleteAttachmentView,
    UpdateAttachmentView,
)
from shared.application.dtos.file_field import FileFieldDTO


@pytest.fixture
def request_factory():
    """Create a request factory."""
    return RequestFactory()


@pytest.fixture
def sample_attachment_file() -> SimpleUploadedFile:
    """Create a sample attachment file."""
    return SimpleUploadedFile(
        "test_file.pdf", b"fake file content", content_type="application/pdf"
    )


@pytest.fixture
def sample_attachment_dto(sample_content_type: ContentType) -> AttachmentDTO:
    """Create a sample AttachmentDTO."""
    attachment_id = str(uuid.uuid4())
    return AttachmentDTO(
        id=attachment_id,
        file=FileFieldDTO(
            file_type="file",
            name="test_file.pdf",
            url="/media/test_file.pdf",
            size=2048,
            width=None,
            height=None,
            content_type="application/pdf",
        ),
        attachment_type="document",
        title="Test Attachment",
        content_type_id=sample_content_type.id,
        object_id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def authenticated_user_with_permissions(db: None):
    """Create an authenticated user with required permissions."""
    from identity.infrastructure.models import User

    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        is_staff=True,
    )

    # Add required permissions
    add_permission = Permission.objects.get(
        codename="add_attachment", content_type__app_label="media_infrastructure"
    )
    change_permission = Permission.objects.get(
        codename="change_attachment", content_type__app_label="media_infrastructure"
    )
    delete_permission = Permission.objects.get(
        codename="delete_attachment", content_type__app_label="media_infrastructure"
    )

    user.user_permissions.add(add_permission, change_permission, delete_permission)
    return user


@pytest.mark.infrastructure
class TestCreateAttachmentView:
    """Tests for CreateAttachmentView."""

    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_get_initial_sets_correct_values(
        self,
        mock_dispatch_command: MagicMock,
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

    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_form_valid_creates_attachment_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that form_valid creates an attachment successfully."""
        mock_dispatch_command.return_value = sample_attachment_dto

        request = request_factory.post(
            "/",
            data={
                "content_type": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "attachment_type": "document",
                "title": "Test Attachment",
            },
        )
        request.FILES["file"] = sample_attachment_file
        request.user = authenticated_user_with_permissions

        view = CreateAttachmentView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
        }

        # Create a mock form
        form = MagicMock()
        form.get_form_data.return_value = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
            "title": "Test Attachment",
        }
        form.files = {"file": sample_attachment_file}
        form.is_valid.return_value = True

        response = view.form_valid(form)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert "Attachment has been created successfully" in data["message"]
        assert data["details"]["is_update"] is False
        assert "attachment" in data["details"]

        # Verify command was dispatched correctly
        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, CreateAttachmentCommand)
        assert call_args.content_type_id == sample_content_type.id
        assert call_args.attachment_type == "document"
        assert call_args.title == "Test Attachment"

    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_form_invalid_returns_response(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
    ):
        """Test that form_invalid returns a response."""
        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = CreateAttachmentView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
        }

        form = MagicMock()
        form.errors = {"file": ["This field is required."]}
        form.is_valid.return_value = False

        response = view.form_invalid(form)

        assert response is not None
        assert hasattr(response, "status_code")

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test that view requires correct permissions."""
        view = CreateAttachmentView()
        assert "media_infrastructure.add_attachment" in view.permission_required


@pytest.mark.infrastructure
class TestUpdateAttachmentView:
    """Tests for UpdateAttachmentView."""

    @patch("media.infrastructure.views.attachment_views.dispatch_query")
    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_get_initial_loads_attachment_data(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that get_initial loads attachment data from query."""
        mock_dispatch_query.return_value = sample_attachment_dto

        view = UpdateAttachmentView()
        view.kwargs = {"attachment_id": sample_attachment_dto.id}

        initial = view.get_initial()

        assert initial["attachment_id"] == sample_attachment_dto.id
        assert initial["content_type"] == sample_attachment_dto.content_type_id
        assert initial["object_id"] == sample_attachment_dto.object_id
        assert initial["attachment_type"] == sample_attachment_dto.attachment_type
        assert initial["title"] == sample_attachment_dto.title

        mock_dispatch_query.assert_called_once()
        call_args = mock_dispatch_query.call_args[0][0]
        assert isinstance(call_args, GetAttachmentByIdQuery)
        assert call_args.attachment_id == sample_attachment_dto.id

    @patch("media.infrastructure.views.attachment_views.dispatch_query")
    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_get_form_sets_attachment_data(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that get_form sets attachment_data on form."""
        mock_dispatch_query.return_value = sample_attachment_dto

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": sample_attachment_dto.id}

        form = view.get_form()

        assert hasattr(form, "attachment_data")
        assert form.attachment_data == sample_attachment_dto

    @patch("media.infrastructure.views.attachment_views.dispatch_query")
    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_form_valid_updates_attachment_with_file(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_file: SimpleUploadedFile,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that form_valid updates an attachment with new file."""
        mock_dispatch_query.return_value = sample_attachment_dto
        updated_dto = AttachmentDTO(
            id=sample_attachment_dto.id,
            file=FileFieldDTO(
                file_type="file",
                name="updated_file.pdf",
                url="/media/updated_file.pdf",
                size=4096,
                width=None,
                height=None,
                content_type="application/pdf",
            ),
            attachment_type=sample_attachment_dto.attachment_type,
            title="Updated Title",
            content_type_id=sample_attachment_dto.content_type_id,
            object_id=sample_attachment_dto.object_id,
            created_at=sample_attachment_dto.created_at,
            updated_at=datetime.now(),
        )
        mock_dispatch_command.return_value = updated_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": sample_attachment_dto.id}

        form = MagicMock()
        form.get_form_data.return_value = {
            "attachment_id": sample_attachment_dto.id,
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
            "title": "Updated Title",
        }
        form.files = {"file": sample_attachment_file}
        form.is_valid.return_value = True

        response = view.form_valid(form)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert "Attachment has been updated successfully" in data["message"]
        assert data["details"]["is_update"] is True

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, UpdateAttachmentCommand)
        assert call_args.attachment_id == uuid.UUID(sample_attachment_dto.id)
        assert call_args.title == "Updated Title"

    @patch("media.infrastructure.views.attachment_views.dispatch_query")
    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_form_valid_updates_attachment_without_file(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that form_valid updates an attachment without new file."""
        mock_dispatch_query.return_value = sample_attachment_dto
        updated_dto = AttachmentDTO(
            id=sample_attachment_dto.id,
            file=sample_attachment_dto.file,
            attachment_type=sample_attachment_dto.attachment_type,
            title="Updated Title",
            content_type_id=sample_attachment_dto.content_type_id,
            object_id=sample_attachment_dto.object_id,
            created_at=sample_attachment_dto.created_at,
            updated_at=datetime.now(),
        )
        mock_dispatch_command.return_value = updated_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": sample_attachment_dto.id}

        form = MagicMock()
        form.get_form_data.return_value = {
            "attachment_id": sample_attachment_dto.id,
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "attachment_type": "document",
            "title": "Updated Title",
        }
        form.files = {}
        form.is_valid.return_value = True

        response = view.form_valid(form)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, UpdateAttachmentCommand)
        assert call_args.file is None

    @patch("media.infrastructure.views.attachment_views.dispatch_query")
    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_form_invalid_returns_response(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that form_invalid returns a response."""
        mock_dispatch_query.return_value = sample_attachment_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdateAttachmentView()
        view.request = request
        view.kwargs = {"attachment_id": sample_attachment_dto.id}

        form = MagicMock()
        form.errors = {"title": ["This field is required."]}
        form.is_valid.return_value = False

        response = view.form_invalid(form)

        assert response is not None
        assert hasattr(response, "status_code")

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test that view requires correct permissions."""
        view = UpdateAttachmentView()
        assert "media_infrastructure.change_attachment" in view.permission_required


@pytest.mark.infrastructure
class TestDeleteAttachmentView:
    """Tests for DeleteAttachmentView."""

    @patch("media.infrastructure.views.attachment_views.dispatch_command")
    def test_post_deletes_attachment_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that POST deletes an attachment successfully."""
        mock_dispatch_command.return_value = sample_attachment_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = DeleteAttachmentView()
        view.request = request
        view.command_class = DeleteAttachmentCommand

        attachment_id = uuid.uuid4()
        response = view.post(request, pk=str(attachment_id))

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert "successfully deleted" in data["message"].lower()
        assert "details" in data

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, DeleteAttachmentCommand)
        assert call_args.pk == attachment_id

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test that view requires correct permissions."""
        view = DeleteAttachmentView()
        assert "media_infrastructure.delete_attachment" in view.permission_required

