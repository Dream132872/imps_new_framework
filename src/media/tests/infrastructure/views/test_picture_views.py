"""Tests for picture views."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse

from media.application.commands import (
    CreatePictureCommand,
    DeletePictureCommand,
    UpdatePictureCommand,
)
from media.application.dtos import PictureDTO
from media.application.queries import GetPictureByIdQuery
from media.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
)
from shared.application.dtos.file_field import FileFieldDTO


@pytest.fixture
def request_factory():
    """Create a request factory."""
    return RequestFactory()


@pytest.fixture
def sample_image_file() -> SimpleUploadedFile:
    """Create a sample image file."""
    return SimpleUploadedFile(
        "test_image.jpg", b"fake image content", content_type="image/jpeg"
    )


@pytest.fixture
def sample_picture_dto(sample_content_type: ContentType) -> PictureDTO:
    """Create a sample PictureDTO."""
    picture_id = str(uuid.uuid4())
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
    add_permission = Permission.objects.get(
        codename="add_picture", content_type__app_label="media_infrastructure"
    )
    change_permission = Permission.objects.get(
        codename="change_picture", content_type__app_label="media_infrastructure"
    )
    delete_permission = Permission.objects.get(
        codename="delete_picture", content_type__app_label="media_infrastructure"
    )

    user.user_permissions.add(add_permission, change_permission, delete_permission)
    return user


@pytest.mark.infrastructure
class TestCreatePictureView:
    """Tests for CreatePictureView."""

    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_get_initial_sets_correct_values(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test that get_initial sets correct values from URL kwargs."""
        view = CreatePictureView()
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
        }

        initial = view.get_initial()

        assert initial["content_type"] == str(sample_content_type.id)
        assert initial["object_id"] == str(view.kwargs["object_id"])
        assert initial["picture_type"] == "main"

    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_form_valid_creates_picture_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
        sample_image_file: SimpleUploadedFile,
        sample_picture_dto: PictureDTO,
    ):
        """Test that form_valid creates a picture successfully."""
        mock_dispatch_command.return_value = sample_picture_dto

        request = request_factory.post(
            "/",
            data={
                "content_type": str(sample_content_type.id),
                "object_id": str(uuid.uuid4()),
                "picture_type": "main",
                "title": "Test Picture",
                "alternative": "Test Alternative",
            },
        )
        request.FILES["image"] = sample_image_file
        request.user = authenticated_user_with_permissions

        view = CreatePictureView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
        }

        # Create a mock form
        form = MagicMock()
        form.get_form_data.return_value = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
            "title": "Test Picture",
            "alternative": "Test Alternative",
        }
        form.files = {"image": sample_image_file}
        form.is_valid.return_value = True

        response = view.form_valid(form)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert "Picture has been created successfully" in data["message"]
        assert data["details"]["is_update"] is False
        assert "picture" in data["details"]

        # Verify command was dispatched correctly
        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, CreatePictureCommand)
        assert call_args.content_type_id == sample_content_type.id
        assert call_args.picture_type == "main"
        assert call_args.title == "Test Picture"
        assert call_args.alternative == "Test Alternative"

    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_form_invalid_returns_response(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test that form_invalid returns a response."""
        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = CreatePictureView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
        }

        form = MagicMock()
        form.errors = {"image": ["This field is required."]}
        form.is_valid.return_value = False

        response = view.form_invalid(form)

        assert response is not None
        assert hasattr(response, "status_code")

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = CreatePictureView()
        assert "media_infrastructure.add_picture" in view.permission_required


@pytest.mark.infrastructure
class TestUpdatePictureView:
    """Tests for UpdatePictureView."""

    @patch("media.infrastructure.views.picture_views.dispatch_query")
    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_get_initial_loads_picture_data(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_picture_dto: PictureDTO,
    ):
        """Test that get_initial loads picture data from query."""
        mock_dispatch_query.return_value = sample_picture_dto

        view = UpdatePictureView()
        view.kwargs = {"picture_id": sample_picture_dto.id}

        initial = view.get_initial()

        assert initial["picture_id"] == sample_picture_dto.id
        assert initial["content_type"] == sample_picture_dto.content_type_id
        assert initial["object_id"] == sample_picture_dto.object_id
        assert initial["picture_type"] == sample_picture_dto.picture_type
        assert initial["title"] == sample_picture_dto.title
        assert initial["alternative"] == sample_picture_dto.alternative

        mock_dispatch_query.assert_called_once()
        call_args = mock_dispatch_query.call_args[0][0]
        assert isinstance(call_args, GetPictureByIdQuery)
        assert call_args.picture_id == sample_picture_dto.id

    @patch("media.infrastructure.views.picture_views.dispatch_query")
    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_get_form_sets_picture_data(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_picture_dto: PictureDTO,
    ):
        """Test that get_form sets picture_data on form."""
        mock_dispatch_query.return_value = sample_picture_dto

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": sample_picture_dto.id}

        form = view.get_form()

        assert hasattr(form, "picture_data")
        assert form.picture_data == sample_picture_dto

    @patch("media.infrastructure.views.picture_views.dispatch_query")
    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_form_valid_updates_picture_with_image(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
        sample_image_file: SimpleUploadedFile,
        sample_picture_dto: PictureDTO,
    ):
        """Test that form_valid updates a picture with new image."""
        mock_dispatch_query.return_value = sample_picture_dto
        updated_dto = PictureDTO(
            id=sample_picture_dto.id,
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
        mock_dispatch_command.return_value = updated_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": sample_picture_dto.id}

        form = MagicMock()
        form.get_form_data.return_value = {
            "picture_id": sample_picture_dto.id,
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
            "title": "Updated Title",
            "alternative": "Updated Alternative",
        }
        form.files = {"image": sample_image_file}
        form.is_valid.return_value = True

        response = view.form_valid(form)

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert "Picture has been updated successfully" in data["message"]
        assert data["details"]["is_update"] is True

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, UpdatePictureCommand)
        assert call_args.picture_id == uuid.UUID(sample_picture_dto.id)
        assert call_args.title == "Updated Title"

    @patch("media.infrastructure.views.picture_views.dispatch_query")
    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_form_valid_updates_picture_without_image(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
        sample_picture_dto: PictureDTO,
    ):
        """Test that form_valid updates a picture without new image."""
        mock_dispatch_query.return_value = sample_picture_dto
        updated_dto = PictureDTO(
            id=sample_picture_dto.id,
            image=sample_picture_dto.image,
            picture_type=sample_picture_dto.picture_type,
            title="Updated Title",
            alternative="Updated Alternative",
            content_type_id=sample_picture_dto.content_type_id,
            object_id=sample_picture_dto.object_id,
            created_at=sample_picture_dto.created_at,
            updated_at=datetime.now(),
        )
        mock_dispatch_command.return_value = updated_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": sample_picture_dto.id}

        form = MagicMock()
        form.get_form_data.return_value = {
            "picture_id": sample_picture_dto.id,
            "content_type": str(sample_content_type.id),
            "object_id": str(uuid.uuid4()),
            "picture_type": "main",
            "title": "Updated Title",
            "alternative": "Updated Alternative",
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
        assert isinstance(call_args, UpdatePictureCommand)
        assert call_args.image is None

    @patch("media.infrastructure.views.picture_views.dispatch_query")
    @patch("media.infrastructure.views.picture_views.dispatch_command")
    def test_form_invalid_returns_response(
        self,
        mock_dispatch_command: MagicMock,
        mock_dispatch_query: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_picture_dto: PictureDTO,
    ):
        """Test that form_invalid returns a response."""
        mock_dispatch_query.return_value = sample_picture_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": sample_picture_dto.id}

        form = MagicMock()
        form.errors = {"title": ["This field is required."]}
        form.is_valid.return_value = False

        response = view.form_invalid(form)

        assert response is not None
        assert hasattr(response, "status_code")

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = UpdatePictureView()
        assert "media_infrastructure.change_picture" in view.permission_required


@pytest.mark.infrastructure
class TestDeletePictureView:
    """Tests for DeletePictureView."""

    @patch("shared.infrastructure.views.generics.dispatch_command")
    def test_post_deletes_picture_successfully(
        self,
        mock_dispatch_command: MagicMock,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_picture_dto: PictureDTO,
    ):
        """Test that POST deletes a picture successfully."""
        mock_dispatch_command.return_value = sample_picture_dto

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = DeletePictureView()
        view.request = request
        view.command_class = DeletePictureCommand

        picture_id = uuid.uuid4()
        response = view.post(request, pk=str(picture_id))

        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert "details" in data
        assert "message" in data

        mock_dispatch_command.assert_called_once()
        call_args = mock_dispatch_command.call_args[0][0]
        assert isinstance(call_args, DeletePictureCommand)
        assert call_args.pk == picture_id

    def test_permission_required(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
    ):
        """Test that view requires correct permissions."""
        view = DeletePictureView()
        assert "media_infrastructure.delete_picture" in view.permission_required

