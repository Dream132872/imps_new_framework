"""Integration tests for chunk upload views."""

import os
import uuid
from io import BytesIO

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from PIL import Image

from identity.infrastructure.models.user import User
from media.infrastructure.models import (
    Attachment as AttachmentModel,
    ChunkUpload as ChunkUploadModel,
    Picture as PictureModel,
)
from media.infrastructure.views import (
    CompleteAttachmentChunkUploadView,
    CompletePictureChunkUploadView,
    CreateChunkUploadView,
    GetChunkUploadStatusView,
    UploadChunkView,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


def _create_image_file(name: str = "test.png") -> SimpleUploadedFile:
    """Helper to create a valid image file for testing."""
    buffer = BytesIO()
    Image.new("RGB", (100, 100), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(
        name=name, content=buffer.read(), content_type="image/png"
    )


@pytest.fixture
def request_factory():
    """Create a request factory."""
    return RequestFactory()


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


@pytest.mark.integration
@pytest.mark.infrastructure
class TestCreateChunkUploadViewIntegration:
    """Integration tests for CreateChunkUploadView."""

    def test_create_chunk_upload_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
    ):
        """Test creating a chunk upload through the view with real command handler."""
        # Arrange
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

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert "upload_id" in data
        assert "offset" in data
        assert data["offset"] == 0

        # Verify chunk upload was actually created in database
        upload_id = data["upload_id"]
        chunk_upload = ChunkUploadModel.objects.get(upload_id=upload_id)
        assert chunk_upload.filename == "test_file.jpg"
        assert chunk_upload.total_size == 1024
        assert chunk_upload.uploaded_size == 0


@pytest.mark.integration
@pytest.mark.infrastructure
class TestUploadChunkViewIntegration:
    """Integration tests for UploadChunkView."""

    def test_upload_chunk_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test uploading a chunk through the view with real command handler."""
        # Arrange: Create a chunk upload first
        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=str(uuid.uuid4()),
            filename="test_file.jpg",
            total_size=1024,
            uploaded_size=0,
        )

        chunk_data = b"chunk data content"
        chunk_file = SimpleUploadedFile(
            "chunk.bin", chunk_data, content_type="application/octet-stream"
        )

        request = request_factory.post(
            "/",
            data={
                "upload_id": chunk_upload.upload_id,
                "offset": "0",
            },
        )
        request.FILES["chunk"] = chunk_file
        request.user = authenticated_user_with_permissions

        view = UploadChunkView()
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert "upload_id" in data
        assert "offset" in data
        assert "progress" in data
        assert "completed" in data

        # Verify chunk was actually uploaded
        updated_chunk_upload = ChunkUploadModel.objects.get(
            upload_id=chunk_upload.upload_id
        )
        assert updated_chunk_upload.uploaded_size > 0
        assert updated_chunk_upload.chunk_count > 0


@pytest.mark.integration
@pytest.mark.infrastructure
class TestGetChunkUploadStatusViewIntegration:
    """Integration tests for GetChunkUploadStatusView."""

    def test_get_chunk_upload_status_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test getting chunk upload status through the view with real query handler."""
        # Arrange: Create a chunk upload
        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=str(uuid.uuid4()),
            filename="test_file.jpg",
            total_size=1024,
            uploaded_size=512,
            chunk_count=1,
        )

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = GetChunkUploadStatusView()
        response = view.get(request, upload_id=chunk_upload.upload_id)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["upload_id"] == chunk_upload.upload_id
        assert data["filename"] == chunk_upload.filename
        assert data["total_size"] == chunk_upload.total_size
        assert data["uploaded_size"] == chunk_upload.uploaded_size
        assert "progress" in data
        assert "completed" in data


@pytest.mark.integration
@pytest.mark.infrastructure
class TestCompletePictureChunkUploadViewIntegration:
    """Integration tests for CompletePictureChunkUploadView."""

    def test_complete_picture_chunk_upload_creates_picture(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
    ):
        """Test completing chunk upload and creating a picture through the view."""
        # Arrange: Create a chunk upload with some chunks
        upload_id = str(uuid.uuid4())
        filename = "test_image.png"
        name, ext = os.path.splitext(filename)
        temp_file_path = f"chunks/{upload_id}/file{ext}"

        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=upload_id,
            filename=filename,
            total_size=1024,
            uploaded_size=1024,
            chunk_count=2,
            temp_file_path=temp_file_path,
        )

        # Write some data to temp file (simulating chunks)
        from django.core.files.storage import default_storage

        default_storage.save(temp_file_path, BytesIO(b"fake image content"))

        object_id = str(uuid.uuid4())
        request = request_factory.post(
            "/",
            data={
                "upload_id": chunk_upload.upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "main",
                "title": "Test Picture",
                "alternative": "Test Alternative",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is False
        assert "picture" in data["details"]

        # Verify picture was actually created
        picture_data = data["details"]["picture"]
        picture_id = picture_data["id"]
        picture = PictureModel.objects.get(id=picture_id)
        assert picture.title == "Test Picture"
        assert picture.alternative == "Test Alternative"
        assert picture.picture_type == "main"
        assert picture.object_id == object_id

    def test_complete_picture_chunk_upload_updates_picture(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test completing chunk upload and updating an existing picture."""
        # Arrange: Create an existing picture
        image_file = _create_image_file("original.png")
        object_id = str(uuid.uuid4())

        existing_picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=object_id,
            picture_type="main",
            title="Original Title",
            alternative="Original Alternative",
        )

        # Create a chunk upload
        upload_id = str(uuid.uuid4())
        filename = "updated_image.png"
        name, ext = os.path.splitext(filename)
        temp_file_path = f"chunks/{upload_id}/file{ext}"

        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=upload_id,
            filename=filename,
            total_size=2048,
            uploaded_size=2048,
            chunk_count=2,
            temp_file_path=temp_file_path,
        )

        # Write some data to temp file
        from django.core.files.storage import default_storage

        default_storage.save(temp_file_path, BytesIO(b"updated image content"))

        request = request_factory.post(
            "/",
            data={
                "upload_id": chunk_upload.upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "gallery",
                "title": "Updated Title",
                "alternative": "Updated Alternative",
                "picture_id": str(existing_picture.id),
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is True

        # Verify picture was actually updated
        updated_picture = PictureModel.objects.get(id=existing_picture.id)
        assert updated_picture.title == "Updated Title"
        assert updated_picture.alternative == "Updated Alternative"
        assert updated_picture.picture_type == "gallery"


@pytest.mark.integration
@pytest.mark.infrastructure
class TestCompleteAttachmentChunkUploadViewIntegration:
    """Integration tests for CompleteAttachmentChunkUploadView."""

    def test_complete_attachment_chunk_upload_creates_attachment(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test completing chunk upload and creating an attachment through the view."""
        # Arrange: Create a chunk upload with some chunks
        upload_id = str(uuid.uuid4())
        filename = "test_file.pdf"
        name, ext = os.path.splitext(filename)
        temp_file_path = f"chunks/{upload_id}/file{ext}"

        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=upload_id,
            filename=filename,
            total_size=2048,
            uploaded_size=2048,
            chunk_count=2,
            temp_file_path=temp_file_path,
        )

        # Write some data to temp file
        from django.core.files.storage import default_storage

        default_storage.save(temp_file_path, BytesIO(b"fake file content"))

        object_id = str(uuid.uuid4())
        request = request_factory.post(
            "/",
            data={
                "upload_id": chunk_upload.upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "document",
                "title": "Test Attachment",
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompleteAttachmentChunkUploadView()
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is False
        assert "attachment" in data["details"]

        # Verify attachment was actually created
        attachment_data = data["details"]["attachment"]
        attachment_id = attachment_data["id"]
        attachment = AttachmentModel.objects.get(id=attachment_id)
        assert attachment.title == "Test Attachment"
        assert attachment.attachment_type == "document"
        assert attachment.object_id == object_id

    def test_complete_attachment_chunk_upload_updates_attachment(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test completing chunk upload and updating an existing attachment."""
        # Arrange: Create an existing attachment
        file = SimpleUploadedFile(
            "original.pdf", b"original content", content_type="application/pdf"
        )
        object_id = str(uuid.uuid4())

        existing_attachment = AttachmentModel.objects.create(
            file=file,
            content_type=sample_content_type,
            object_id=object_id,
            attachment_type="document",
            title="Original Title",
        )

        # Create a chunk upload
        upload_id = str(uuid.uuid4())
        filename = "updated_file.pdf"
        name, ext = os.path.splitext(filename)
        temp_file_path = f"chunks/{upload_id}/file{ext}"

        chunk_upload = ChunkUploadModel.objects.create(
            upload_id=upload_id,
            filename=filename,
            total_size=4096,
            uploaded_size=4096,
            chunk_count=2,
            temp_file_path=temp_file_path,
        )

        # Write some data to temp file
        from django.core.files.storage import default_storage

        default_storage.save(temp_file_path, BytesIO(b"updated file content"))

        request = request_factory.post(
            "/",
            data={
                "upload_id": chunk_upload.upload_id,
                "content_type_id": str(sample_content_type.id),
                "object_id": object_id,
                "attachment_type": "archive",
                "title": "Updated Title",
                "attachment_id": str(existing_attachment.id),
            },
        )
        request.user = authenticated_user_with_permissions

        view = CompleteAttachmentChunkUploadView()
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["details"]["is_update"] is True

        # Verify attachment was actually updated
        updated_attachment = AttachmentModel.objects.get(id=existing_attachment.id)
        assert updated_attachment.title == "Updated Title"
        assert updated_attachment.attachment_type == "archive"

