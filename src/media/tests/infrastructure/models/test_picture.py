# """Test picture model."""

# import uuid
# from unittest.mock import MagicMock, patch

# import pytest
# from django.contrib.contenttypes.models import ContentType
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test import override_settings
# from pytest_mock import MockerFixture

# from media.infrastructure.models.picture import Picture as PictureModel
# from media.infrastructure.repositories import DjangoPictureRepository

# # @pytest.mark.infrastructure
# # @pytest.mark.slow
# # @pytest.mark.unit
# # def test_picture_items(
# #     sample_picture_model: PictureModel, mock_picture_repository: MagicMock
# # ):
# #     assert sample_picture_model.title == "title"


# class Calculator:
#     def sum(self, a: int | float, b: int | float):
#         return a + b


# @pytest.mark.unit
# def test_calculator(mocker: MockerFixture):
#     calculator = Calculator()

#     spy = mocker.spy(calculator, "sum")

#     result = calculator.sum(1, 2)

#     assert result == 3
#     spy.assert_called_with(1, 2)
#     assert spy.call_count == 1


# @pytest.mark.unit
# def test_mocking(mocker: MockerFixture):
#     mock = mocker.MagicMock()

#     mock.method("first")
#     mock.method("second")
#     mock.method("third")

#     # Check call count
#     assert mock.method.call_count == 3

#     # Check all calls
#     assert mock.method.call_args_list == [
#         mocker.call("first"),
#         mocker.call("second"),
#         mocker.call("third"),
#     ]

#     # Check last call
#     assert mock.method.call_args == mocker.call("third")


# @pytest.mark.integration
# @pytest.mark.django_db()
# @patch("django.core.files.storage.default_storage")
# def test_picture_creation(
#     mock_storage: MagicMock, sample_picture_model: PictureModel
# ) -> None:
#     """Test picture creation without saving files to disk"""
#     # Mock the storage to prevent actual file saving
#     mock_storage.save.return_value = "images/test_image.jpg"
#     mock_storage.url.return_value = "/media/images/test_image.jpg"
#     mock_storage.path.return_value = "/fake/path/images/test_image.jpg"
#     mock_storage.size.return_value = 1024
#     mock_storage.exists.return_value = True

#     # arrange
#     picture = sample_picture_model

#     # act
#     picture.save()

#     # assert
#     assert picture.id is not None
#     assert picture.display_order == 1
#     # Verify that storage.save was called (but mocked, so no real file is created)
#     # Note: Django may call save() multiple times, so we check if it was called at least once
#     assert mock_storage.save.called
