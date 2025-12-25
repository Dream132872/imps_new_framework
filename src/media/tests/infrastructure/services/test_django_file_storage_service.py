"""Integration tests for DjangoFileStorageService"""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from media.infrastructure.services import DjangoFileStorageService


@pytest.mark.infrastructure
@pytest.mark.integration
class TestDjangoFileStorageService:
    """Integration tests for DjangoFileStorageService"""

    @pytest.fixture
    def service(self) -> DjangoFileStorageService:
        """Create service instance"""
        return DjangoFileStorageService()

    def test_save_image_with_valid_content(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving an image with valid content"""

        # Arrange
        image_content = b"fake image content"
        image_file = BytesIO(image_content)
        image_file.name = "test_image.jpg"

        # Act
        saved_path = service.save_image(image_file)

        # Assert
        assert saved_path != ""
        assert saved_path.startswith("images/")
        assert saved_path.endswith(".jpg")
        assert service.image_exists(saved_path)

    def test_save_image_with_no_content_returns_empty_string(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving an image with no content returns empty string"""

        # Arrange
        empty_file = BytesIO(b"")

        # Act
        saved_path = service.save_image(empty_file)

        # Assert
        assert saved_path == ""

    def test_save_image_with_none_returns_empty_string(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving None returns empty string"""

        # Act
        saved_path = service.save_image(None)  # type: ignore

        # Assert
        assert saved_path == ""

    def test_save_image_with_different_extensions(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving images with different extensions"""

        # Arrange
        extensions = [".jpg", ".png", ".gif", ".jpeg", ".webp"]

        for ext in extensions:
            image_file = BytesIO(b"fake image content")
            image_file.name = f"test_image{ext}"

            # Act
            saved_path = service.save_image(image_file)

            # Assert
            assert saved_path.endswith(ext)
            assert service.image_exists(saved_path)

    def test_save_image_without_name_uses_default_extension(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving image without name uses default .jpg extension"""

        # Arrange
        image_file = BytesIO(b"fake image content")
        # Don't set name attribute

        # Act
        saved_path = service.save_image(image_file)

        # Assert
        assert saved_path.endswith(".jpg")
        assert service.image_exists(saved_path)

    def test_save_image_resets_file_position(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test that save_image resets file position to start"""

        # Arrange
        image_content = b"fake image content"
        image_file = BytesIO(image_content)
        image_file.name = "test_image.jpg"
        image_file.read()  # Move position forward

        # Act
        saved_path = service.save_image(image_file)

        # Assert
        assert saved_path != ""
        assert service.image_exists(saved_path)

    def test_delete_image_with_existing_file(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test deleting an existing image"""

        # Arrange
        image_file = BytesIO(b"fake image content")
        image_file.name = "test_image.jpg"
        saved_path = service.save_image(image_file)
        assert service.image_exists(saved_path)

        # Act
        service.delete_image(saved_path)

        # Assert
        assert not service.image_exists(saved_path)

    def test_delete_image_with_non_existing_file(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test deleting a non-existing image doesn't raise error"""

        # Arrange
        non_existent_path = "images/non_existent.jpg"

        # Act & Assert - should not raise error
        service.delete_image(non_existent_path)

    def test_image_exists_returns_true_for_existing(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test image_exists returns True for existing image"""

        # Arrange
        image_file = BytesIO(b"fake image content")
        image_file.name = "test_image.jpg"
        saved_path = service.save_image(image_file)

        # Act
        exists = service.image_exists(saved_path)

        # Assert
        assert exists is True

    def test_image_exists_returns_false_for_non_existing(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test image_exists returns False for non-existing image"""

        # Arrange
        non_existent_path = "images/non_existent.jpg"

        # Act
        exists = service.image_exists(non_existent_path)

        # Assert
        assert exists is False

    def test_image_exists_returns_false_for_empty_path(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test image_exists returns False for empty path"""

        # Act
        exists = service.image_exists("")

        # Assert
        assert exists is False

    def test_image_exists_returns_false_for_none(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test image_exists returns False for None"""

        # Act
        exists = service.image_exists(None)  # type: ignore

        # Assert
        assert exists is False

    def test_save_file_with_valid_content(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving a file with valid content"""

        # Arrange
        file_content = b"fake file content"
        file_obj = BytesIO(file_content)
        file_obj.name = "test_file.pdf"

        # Act
        saved_path = service.save_file(file_obj)

        # Assert
        assert saved_path != ""
        assert saved_path.startswith("attachments/")
        assert saved_path.endswith(".pdf")
        assert service.file_exists(saved_path)

    def test_save_file_with_different_extensions(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving files with different extensions"""

        # Arrange
        extensions = [".pdf", ".doc", ".zip", ".rar", ".txt"]

        for ext in extensions:
            file_obj = BytesIO(b"fake file content")
            file_obj.name = f"test_file{ext}"

            # Act
            saved_path = service.save_file(file_obj)

            # Assert
            assert saved_path.endswith(ext)
            assert service.file_exists(saved_path)

    def test_save_file_without_name_uses_default_extension(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test saving file without name uses default .bin extension"""

        # Arrange
        file_obj = BytesIO(b"fake file content")
        # Don't set name attribute

        # Act
        saved_path = service.save_file(file_obj)

        # Assert
        assert saved_path.endswith(".bin")
        assert service.file_exists(saved_path)

    def test_save_file_resets_file_position(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test that save_file resets file position to start"""

        # Arrange
        file_content = b"fake file content"
        file_obj = BytesIO(file_content)
        file_obj.name = "test_file.pdf"
        file_obj.read()  # Move position forward

        # Act
        saved_path = service.save_file(file_obj)

        # Assert
        assert saved_path != ""
        assert service.file_exists(saved_path)

    def test_delete_file_with_existing_file(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test deleting an existing file"""

        # Arrange
        file_obj = BytesIO(b"fake file content")
        file_obj.name = "test_file.pdf"
        saved_path = service.save_file(file_obj)
        assert service.file_exists(saved_path)

        # Act
        service.delete_file(saved_path)

        # Assert
        assert not service.file_exists(saved_path)

    def test_delete_file_with_non_existing_file(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test deleting a non-existing file doesn't raise error"""

        # Arrange
        non_existent_path = "attachments/non_existent.pdf"

        # Act & Assert - should not raise error
        service.delete_file(non_existent_path)

    def test_file_exists_returns_true_for_existing(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test file_exists returns True for existing file"""

        # Arrange
        file_obj = BytesIO(b"fake file content")
        file_obj.name = "test_file.pdf"
        saved_path = service.save_file(file_obj)

        # Act
        exists = service.file_exists(saved_path)

        # Assert
        assert exists is True

    def test_file_exists_returns_false_for_non_existing(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test file_exists returns False for non-existing file"""

        # Arrange
        non_existent_path = "attachments/non_existent.pdf"

        # Act
        exists = service.file_exists(non_existent_path)

        # Assert
        assert exists is False

    def test_file_exists_returns_false_for_empty_path(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test file_exists returns False for empty path"""

        # Act
        exists = service.file_exists("")

        # Assert
        assert exists is False

    def test_file_exists_returns_false_for_none(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test file_exists returns False for None"""

        # Act
        exists = service.file_exists(None)  # type: ignore

        # Assert
        assert exists is False

    def test_save_image_with_simple_uploaded_file(
        self,
        service: DjangoFileStorageService,
        sample_image_file: SimpleUploadedFile,
        db: None,
    ) -> None:
        """Test saving image with SimpleUploadedFile"""

        # Act
        saved_path = service.save_image(sample_image_file)

        # Assert
        assert saved_path != ""
        assert saved_path.startswith("images/")
        assert service.image_exists(saved_path)

    def test_save_file_with_simple_uploaded_file(
        self,
        service: DjangoFileStorageService,
        sample_attachment_file: SimpleUploadedFile,
        db: None,
    ) -> None:
        """Test saving file with SimpleUploadedFile"""

        # Act
        saved_path = service.save_file(sample_attachment_file)

        # Assert
        assert saved_path != ""
        assert saved_path.startswith("attachments/")
        assert service.file_exists(saved_path)

    def test_save_image_generates_unique_paths(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test that save_image generates unique paths for each save"""

        # Arrange
        image_file1 = BytesIO(b"fake image content 1")
        image_file1.name = "test_image.jpg"
        image_file2 = BytesIO(b"fake image content 2")
        image_file2.name = "test_image.jpg"

        # Act
        path1 = service.save_image(image_file1)
        path2 = service.save_image(image_file2)

        # Assert
        assert path1 != path2
        assert service.image_exists(path1)
        assert service.image_exists(path2)

    def test_save_file_generates_unique_paths(
        self,
        service: DjangoFileStorageService,
        db: None,
    ) -> None:
        """Test that save_file generates unique paths for each save"""

        # Arrange
        file_obj1 = BytesIO(b"fake file content 1")
        file_obj1.name = "test_file.pdf"
        file_obj2 = BytesIO(b"fake file content 2")
        file_obj2.name = "test_file.pdf"

        # Act
        path1 = service.save_file(file_obj1)
        path2 = service.save_file(file_obj2)

        # Assert
        assert path1 != path2
        assert service.file_exists(path1)
        assert service.file_exists(path2)

