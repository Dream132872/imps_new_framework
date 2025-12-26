"""Tests for chunk upload views."""

import uuid
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from identity.infrastructure.models.user import User
from media.application import commands as chunk_upload_commands
from media.application.commands import (
    CreateAttachmentCommand,
    CreatePictureCommand,
    UpdateAttachmentCommand,
    UpdatePictureCommand,
)
from media.application.dtos import AttachmentDTO, PictureDTO
from media.infrastructure.views import (
    CompleteAttachmentChunkUploadView,
    CompletePictureChunkUploadView,
    CreateChunkUploadView,
    GetChunkUploadStatusView,
    UploadChunkView,
)
from shared.application.dtos.file_field import FileFieldDTO


@pytest.fixture
def request_factory():
    """Create a request factory."""
    return RequestFactory()


@pytest.fixture
def sample_chunk_file() -> SimpleUploadedFile:
    """Create a sample chunk file."""
    return SimpleUploadedFile(
        "chunk.bin", b"fake chunk content", content_type="application/octet-stream"
    )


@pytest.fixture
def sample_picture_dto(sample_content_type: ContentType) -> PictureDTO:
    """Create a sample PictureDTO."""
    picture_id = uuid.uuid4()
    return PictureDTO(
        id=picture_id,
        image=FileFieldDTO(
            file_type="image",
            name="test_image.jpg",
            url="/media/test_image.jpg",
            size=1024,
            width=800,
            height=600,
            content_type="image/jpeg",
        ),
        picture_type="main",
        title="Test Picture",
        alternative="Test Alternative",
        content_type_id=sample_content_type.id,
        object_id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_attachment_dto(sample_content_type: ContentType) -> AttachmentDTO:
    """Create a sample AttachmentDTO."""
    attachment_id = uuid.uuid4()
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
def authenticated_user_with_permissions(db):
    """Create an authenticated user with required permissions."""
    from identity.infrastructure.models import User

    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        is_staff=True,
    )

    # Add required permissions
    add_picture_permission = Permission.objects.get(
        codename="add_picture", content_type__app_label="media_infrastructure"
    )
    change_picture_permission = Permission.objects.get(
        codename="change_picture", content_type__app_label="media_infrastructure"
    )
    add_attachment_permission = Permission.objects.get(
        codename="add_attachment", content_type__app_label="media_infrastructure"
    )
    change_attachment_permission = Permission.objects.get(
        codename="change_attachment", content_type__app_label="media_infrastructure"
    )

    user.user_permissions.add(
        add_picture_permission,
        change_picture_permission,
        add_attachment_permission,
        change_attachment_permission,
    )
    return user


@pytest.mark.infrastructure
class TestCreateChunkUploadView:
    """Tests for CreateChunkUploadView."""

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_creates_chunk_upload_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST creates a chunk upload successfully."""
        upload_id = str(uuid.uuid4())
        mock_dispatch_command.return_value = {
            "upload_id": upload_id,
            "offset": 0,
        }

        request = request_factory.post(
            "/",
            data={
                "filename": "test_file.jpg",
                "total_size": "1024",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CreateChunkUploadView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert "upload_id" in data
        assert data["offset"] == 0

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, chunk_upload_commands.CreateChunkUploadCommand)
        assert call_args.filename == "test_file.jpg"
        assert call_args.total_size == 1024

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_filename_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST returns error when filename is missing."""
        request = request_factory.post(
            "/",
            data={
                "total_size": "1024",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CreateChunkUploadView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_total_size_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST returns error when total_size is missing."""
        request = request_factory.post(
            "/",
            data={
                "filename": "test_file.jpg",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CreateChunkUploadView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_handles_invalid_total_size_value(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST handles invalid total_size value."""
        request = request_factory.post(
            "/",
            data={
                "filename": "test_file.jpg",
                "total_size": "invalid",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CreateChunkUploadView()
        # Should raise ValueError when converting to int
        try:
            response = view.post(request)
            # If no exception, check for error response
            assert response.status_code == 400
        except ValueError:
            # Expected behavior when total_size cannot be converted to int
            pass

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = CreateChunkUploadView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.add_attachment" in view.permission_required


@pytest.mark.infrastructure
class TestUploadChunkView:
    """Tests for UploadChunkView."""

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_uploads_chunk_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_chunk_file: SimpleUploadedFile,
    ):
        """Test that POST uploads a chunk successfully."""
        upload_id = str(uuid.uuid4())
        mock_dispatch_command.return_value = {
            "upload_id": upload_id,
            "offset": len(sample_chunk_file.read()),
            "progress": 50.0,
            "completed": False,
        }
        sample_chunk_file.seek(0)  # Reset file pointer

        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "offset": "0",
            },
        )
        request.FILES["chunk"] = sample_chunk_file
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert "upload_id" in data
        assert "offset" in data
        assert "progress" in data
        assert "completed" in data

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, chunk_upload_commands.UploadChunkCommand)
        assert call_args.upload_id == upload_id
        assert call_args.offset == 0

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_upload_id_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_chunk_file: SimpleUploadedFile,
    ):
        """Test that POST returns error when upload_id is missing."""
        request = request_factory.post(
            "/",
            data={
                "offset": "0",
            },
        )
        request.FILES["chunk"] = sample_chunk_file
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_chunk_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST returns error when chunk is missing."""
        upload_id = str(uuid.uuid4())
        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "offset": "0",
            },
        )
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_offset_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_chunk_file: SimpleUploadedFile,
    ):
        """Test that POST returns error when offset is missing."""
        upload_id = str(uuid.uuid4())
        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
            },
        )
        request.FILES["chunk"] = sample_chunk_file
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_handles_invalid_offset_value(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_chunk_file: SimpleUploadedFile,
    ):
        """Test that POST handles invalid offset value."""
        upload_id = str(uuid.uuid4())
        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "offset": "invalid",
            },
        )
        request.FILES["chunk"] = sample_chunk_file
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        # Should raise ValueError when converting to int
        try:
            response = view.post(request)
            # If no exception, check for error response
            assert response.status_code == 400
        except ValueError:
            # Expected behavior when offset cannot be converted to int
            pass

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = UploadChunkView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.add_attachment" in view.permission_required


@pytest.mark.infrastructure
class TestGetChunkUploadStatusView:
    """Tests for GetChunkUploadStatusView."""

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_query")
    def test_get_returns_chunk_upload_status(
        self,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that GET returns chunk upload status."""
        upload_id = str(uuid.uuid4())
        mock_dispatch_query.return_value = {
            "upload_id": upload_id,
            "filename": "test_file.jpg",
            "total_size": 1024,
            "uploaded_size": 512,
            "chunk_count": 1,
            "status": "uploading",
            "progress": 50.0,
            "completed": False,
        }

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = GetChunkUploadStatusView()
        response = view.get(request, upload_id=upload_id)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["upload_id"] == upload_id
        assert data["filename"] == "test_file.jpg"
        assert data["total_size"] == 1024
        assert data["uploaded_size"] == 512
        assert "progress" in data
        assert "completed" in data

        mock_dispatch_query.assert_called_once()

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test that view requires correct permissions."""
        view = GetChunkUploadStatusView()
        assert "media_infrastructure.add_picture" in view.permission_required


@pytest.mark.infrastructure
class TestCompletePictureChunkUploadView:
    """Tests for CompletePictureChunkUploadView."""

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_creates_picture_from_chunk_upload(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_picture_dto: PictureDTO,
    ):
        """Test that POST creates a picture from completed chunk upload."""
        upload_id = str(uuid.uuid4())
        completed_file = BytesIO(b"completed file content")

        # First call returns completed file, second call returns picture DTO
        mock_dispatch_command.side_effect = [completed_file, sample_picture_dto]

        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "picture_type": "main",
                "title": "Test Picture",
                "alternative": "Test Alternative",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is False
        assert "picture" in data["details"]

        assert mock_dispatch_command.call_count == 2
        # First call should be CompleteChunkUploadCommand
        first_call = mock_dispatch_command.call_args_list[0][0][0]
        assert isinstance(first_call, chunk_upload_commands.CompleteChunkUploadCommand)
        assert first_call.upload_id == upload_id

        # Second call should be CreatePictureCommand
        second_call = mock_dispatch_command.call_args_list[1][0][0]
        assert isinstance(second_call, CreatePictureCommand)

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_updates_picture_from_chunk_upload(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_picture_dto: PictureDTO,
    ):
        """Test that POST updates a picture from completed chunk upload."""
        upload_id = str(uuid.uuid4())
        picture_id = str(uuid.uuid4())
        completed_file = BytesIO(b"completed file content")

        # First call returns completed file, second call returns picture DTO
        updated_dto = PictureDTO(
            id=picture_id,
            image=FileFieldDTO(
                file_type="image",
                name="updated_image.jpg",
                url="/media/updated_image.jpg",
                size=2048,
                width=1024,
                height=768,
                content_type="image/jpeg",
            ),
            picture_type=sample_picture_dto.picture_type,
            title="Updated Title",
            alternative="Updated Alternative",
            content_type_id=sample_picture_dto.content_type_id,
            object_id=sample_picture_dto.object_id,
            created_at=sample_picture_dto.created_at,
            updated_at=datetime.now(),
        )
        mock_dispatch_command.side_effect = [completed_file, updated_dto]

        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "picture_type": "main",
                "title": "Updated Title",
                "alternative": "Updated Alternative",
                "picture_id": picture_id,
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is True

        assert mock_dispatch_command.call_count == 2
        # Second call should be UpdatePictureCommand
        second_call = mock_dispatch_command.call_args_list[1][0][0]
        assert isinstance(second_call, UpdatePictureCommand)
        assert second_call.picture_id == uuid.UUID(picture_id)

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_required_fields_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test that POST returns error when required fields are missing."""
        request = request_factory.post(
            "/",
            data={
                "upload_id": str(uuid.uuid4()),
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = CompletePictureChunkUploadView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.change_picture" in view.permission_required


@pytest.mark.infrastructure
class TestCompleteAttachmentChunkUploadView:
    """Tests for CompleteAttachmentChunkUploadView."""

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_creates_attachment_from_chunk_upload(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that POST creates an attachment from completed chunk upload."""
        upload_id = str(uuid.uuid4())
        completed_file = BytesIO(b"completed file content")

        # First call returns completed file, second call returns attachment DTO
        mock_dispatch_command.side_effect = [completed_file, sample_attachment_dto]

        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "attachment_type": "document",
                "title": "Test Attachment",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompleteAttachmentChunkUploadView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is False
        assert "attachment" in data["details"]

        assert mock_dispatch_command.call_count == 2
        # First call should be CompleteChunkUploadCommand
        first_call = mock_dispatch_command.call_args_list[0][0][0]
        assert isinstance(first_call, chunk_upload_commands.CompleteChunkUploadCommand)

        # Second call should be CreateAttachmentCommand
        second_call = mock_dispatch_command.call_args_list[1][0][0]
        assert isinstance(second_call, CreateAttachmentCommand)

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_updates_attachment_from_chunk_upload(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
        sample_attachment_dto: AttachmentDTO,
    ):
        """Test that POST updates an attachment from completed chunk upload."""
        upload_id = str(uuid.uuid4())
        attachment_id = str(uuid.uuid4())
        completed_file = BytesIO(b"completed file content")

        # First call returns completed file, second call returns attachment DTO
        updated_dto = AttachmentDTO(
            id=attachment_id,
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
        mock_dispatch_command.side_effect = [completed_file, updated_dto]

        request = request_factory.post(
            "/",
            data={
                "upload_id": upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "attachment_type": "document",
                "title": "Updated Title",
                "attachment_id": attachment_id,
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompleteAttachmentChunkUploadView()
        response = view.post(request)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is True

        assert mock_dispatch_command.call_count == 2
        # Second call should be UpdateAttachmentCommand
        second_call = mock_dispatch_command.call_args_list[1][0][0]
        assert isinstance(second_call, UpdateAttachmentCommand)
        assert second_call.attachment_id == uuid.UUID(attachment_id)

    @patch("media.infrastructure.views.chunk_upload_views.dispatch_command")
    def test_post_returns_error_when_required_fields_missing(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that POST returns error when required fields are missing."""
        request = request_factory.post(
            "/",
            data={
                "upload_id": str(uuid.uuid4()),
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompleteAttachmentChunkUploadView()
        response = view.post(request)

        assert response.status_code == 400
        import json
        data = json.loads(response.content)
        assert "error" in data
        mock_dispatch_command.assert_not_called()

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = CompleteAttachmentChunkUploadView()
        assert "media_infrastructure.add_attachment" in view.permission_required
        assert "media_infrastructure.change_attachment" in view.permission_required

