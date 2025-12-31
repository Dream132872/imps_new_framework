"""Unit tests for chunk upload views.

These tests focus on validation logic and permission checks.
Integration tests cover the full flow in test_chunk_upload_views_integration.py
"""

import uuid

import pytest

from media.infrastructure.views import (
    CompleteAttachmentChunkUploadView,
    CompletePictureChunkUploadView,
    CreateChunkUploadView,
    GetChunkUploadStatusView,
    UploadChunkView,
)


pytestmark = [
    pytest.mark.django_db,
    pytest.mark.unit,
    pytest.mark.infrastructure,
]


class TestCreateChunkUploadView:
    """Tests for CreateChunkUploadView - validation and permissions only."""

    def test_post_returns_error_when_filename_missing(
        self,
        request_factory,
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

    def test_post_returns_error_when_total_size_missing(
        self,
        request_factory,
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

    def test_post_handles_invalid_total_size_value(
        self,
        request_factory,
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
        with pytest.raises(ValueError):
            view.post(request)

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = CreateChunkUploadView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.add_attachment" in view.permission_required


class TestUploadChunkView:
    """Tests for UploadChunkView - validation and permissions only."""

    def test_post_returns_error_when_upload_id_missing(
        self,
        request_factory,
        authenticated_user_with_permissions,
        sample_chunk_file,
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

    def test_post_returns_error_when_chunk_missing(
        self,
        request_factory,
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

    def test_post_returns_error_when_offset_missing(
        self,
        request_factory,
        authenticated_user_with_permissions,
        sample_chunk_file,
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

    def test_post_handles_invalid_offset_value(
        self,
        request_factory,
        authenticated_user_with_permissions,
        sample_chunk_file,
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
        with pytest.raises(ValueError):
            view.post(request)

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = UploadChunkView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.add_attachment" in view.permission_required


class TestGetChunkUploadStatusView:
    """Tests for GetChunkUploadStatusView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = GetChunkUploadStatusView()
        assert "media_infrastructure.add_picture" in view.permission_required


class TestCompletePictureChunkUploadView:
    """Tests for CompletePictureChunkUploadView - validation and permissions only."""

    def test_post_returns_error_when_required_fields_missing(
        self,
        request_factory,
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

        view = CompletePictureChunkUploadView()
        response = view.post(request)

        assert response.status_code == 400
        import json

        data = json.loads(response.content)
        assert "error" in data

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = CompletePictureChunkUploadView()
        assert "media_infrastructure.add_picture" in view.permission_required
        assert "media_infrastructure.change_picture" in view.permission_required


class TestCompleteAttachmentChunkUploadView:
    """Tests for CompleteAttachmentChunkUploadView - validation and permissions only."""

    def test_post_returns_error_when_required_fields_missing(
        self,
        request_factory,
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

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = CompleteAttachmentChunkUploadView()
        assert "media_infrastructure.add_attachment" in view.permission_required
        assert "media_infrastructure.change_attachment" in view.permission_required
