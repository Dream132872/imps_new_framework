"""Integration tests for picture views."""

import uuid
from io import BytesIO

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from media.application.dtos import PictureDTO
from media.infrastructure.forms import UpsertPictureForm
from media.infrastructure.models import Picture as PictureModel
from media.application.commands import DeletePictureCommand
from media.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
)
from shared.application.cqrs import dispatch_query

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


# Fixtures are now in conftest.py


class TestCreatePictureViewIntegration:
    """Integration tests for CreatePictureView."""

    def test_create_picture_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test creating a picture through the view with real command handler."""
        # Arrange
        image_file = _create_image_file("test_image.png")
        object_id = str(uuid.uuid4())

        request = request_factory.post(
            "/",
            data={
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "main",
                "title": "Test Picture",
                "alternative": "Test Alternative",
            },
        )
        request.FILES["image"] = image_file
        request.user = authenticated_user_with_permissions

        view = CreatePictureView()
        view.request = request
        view.kwargs = {
            "content_type": str(sample_content_type.id),
            "object_id": object_id,
            "picture_type": "main",
        }

        # Create form with request data
        form = UpsertPictureForm(
            data={
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "main",
                "title": "Test Picture",
                "alternative": "Test Alternative",
            },
            files={"image": image_file},
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
        assert "picture" in data["details"]

        # Verify picture was actually created in database
        picture_data = data["details"]["picture"]
        picture_id = picture_data["id"]
        picture = PictureModel.objects.get(id=picture_id)
        assert picture.title == "Test Picture"
        assert picture.alternative == "Test Alternative"
        assert picture.picture_type == "main"
        assert picture.object_id == object_id
        assert picture.content_type_id == sample_content_type.id
        assert picture.image.name.startswith("images/")

    def test_get_initial_sets_correct_values(
        self,
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


class TestUpdatePictureViewIntegration:
    """Integration tests for UpdatePictureView."""

    def test_update_picture_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions: User,
        sample_content_type: ContentType,
    ):
        """Test updating a picture through the view with real command handler."""
        # Arrange: Create a picture first
        image_file = _create_image_file("original.png")
        object_id = str(uuid.uuid4())

        original_picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=object_id,
            picture_type="main",
            title="Original Title",
            alternative="Original Alternative",
        )

        # Update with new image and data
        new_image_file = _create_image_file("updated.png")
        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": str(original_picture.id)}

        form = UpsertPictureForm(
            data={
                "picture_id": str(original_picture.id),
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "main",
                "title": "Updated Title",
                "alternative": "Updated Alternative",
            },
            files={"image": new_image_file},
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

        # Verify picture was actually updated in database
        updated_picture = PictureModel.objects.get(id=original_picture.id)
        assert updated_picture.title == "Updated Title"
        assert updated_picture.alternative == "Updated Alternative"
        assert updated_picture.picture_type == "main"
        assert updated_picture.image.name != original_picture.image.name

    def test_update_picture_without_new_image(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test updating a picture without providing a new image."""
        # Arrange: Create a picture first
        image_file = _create_image_file("original.png")
        object_id = str(uuid.uuid4())

        original_picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=object_id,
            picture_type="main",
            title="Original Title",
            alternative="Original Alternative",
        )

        original_image_name = original_picture.image.name

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": str(original_picture.id)}

        form = UpsertPictureForm(
            data={
                "picture_id": str(original_picture.id),
                "content_type": str(sample_content_type.id),
                "object_id": object_id,
                "picture_type": "main",
                "title": "Updated Title",
                "alternative": "Updated Alternative",
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

        # Verify picture was updated but image remained the same
        updated_picture = PictureModel.objects.get(id=original_picture.id)
        assert updated_picture.title == "Updated Title"
        assert updated_picture.alternative == "Updated Alternative"
        assert updated_picture.image.name == original_image_name

    def test_get_initial_loads_picture_data(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test that get_initial loads picture data from query."""
        # Arrange: Create a picture
        image_file = _create_image_file()
        picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            picture_type="main",
            title="Test Title",
            alternative="Test Alternative",
        )

        view = UpdatePictureView()
        view.kwargs = {"picture_id": str(picture.id)}

        # Act
        initial = view.get_initial()

        # Assert
        assert initial["picture_id"] == str(picture.id)
        assert initial["content_type"] == picture.content_type_id
        assert initial["object_id"] == picture.object_id
        assert initial["picture_type"] == picture.picture_type
        assert initial["title"] == picture.title
        assert initial["alternative"] == picture.alternative

    def test_get_form_sets_picture_data(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test that get_form sets picture_data on form."""
        # Arrange: Create a picture
        image_file = _create_image_file()
        picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            picture_type="main",
            title="Test Title",
            alternative="Test Alternative",
        )

        request = request_factory.get("/")
        request.user = authenticated_user_with_permissions

        view = UpdatePictureView()
        view.request = request
        view.kwargs = {"picture_id": str(picture.id)}

        # Act
        form = view.get_form()

        # Assert
        assert hasattr(form, "picture_data")
        picture_dto = form.picture_data
        assert isinstance(picture_dto, PictureDTO)
        assert str(picture_dto.id) == str(picture.id)
        assert picture_dto.title == picture.title


class TestDeletePictureViewIntegration:
    """Integration tests for DeletePictureView."""

    def test_delete_picture_through_view(
        self,
        request_factory: RequestFactory,
        authenticated_user_with_permissions,
        sample_content_type: ContentType,
    ):
        """Test deleting a picture through the view with real command handler."""
        # Arrange: Create a picture
        image_file = _create_image_file()
        picture = PictureModel.objects.create(
            image=image_file,
            content_type=sample_content_type,
            object_id=str(uuid.uuid4()),
            picture_type="main",
            title="Test Picture",
            alternative="Test Alternative",
        )

        picture_id = picture.id

        request = request_factory.post("/")
        request.user = authenticated_user_with_permissions

        view = DeletePictureView()
        view.request = request
        view.command_class = DeletePictureCommand

        # Act
        response = view.post(request, pk=str(picture_id))

        # Assert
        assert response.status_code == 200
        import json

        data = json.loads(response.content)
        assert "details" in data
        assert "message" in data

        # Verify picture was actually deleted from database
        assert not PictureModel.objects.filter(id=picture_id).exists()
