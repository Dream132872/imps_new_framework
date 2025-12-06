"""Test picture model."""

import uuid

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest_mock import MockerFixture

from media.infrastructure.models.picture import Picture as PictureModel
from media.infrastructure.repositories import DjangoPictureRepository

# @pytest.mark.infrastructure
# @pytest.mark.slow
# @pytest.mark.unit
# def test_picture_items(
#     sample_picture_model: PictureModel, mock_picture_repository: MagicMock
# ):
#     assert sample_picture_model.title == "title"


class Calculator:
    def sum(self, a: int | float, b: int | float):
        return a + b


@pytest.mark.unit
def test_calculator(mocker: MockerFixture):
    calculator = Calculator()

    spy = mocker.spy(calculator, "sum")

    result = calculator.sum(1, 2)

    assert result == 3
    spy.assert_called_with(1, 2)
    assert spy.call_count == 1


@pytest.mark.unit
def test_mocking(mocker: MockerFixture):
    mock = mocker.MagicMock()

    mock.method("first")
    mock.method("second")
    mock.method("third")

    # Check call count
    assert mock.method.call_count == 3

    # Check all calls
    assert mock.method.call_args_list == [
        mocker.call("first"),
        mocker.call("second"),
        mocker.call("third"),
    ]

    # Check last call
    assert mock.method.call_args == mocker.call("third")


@pytest.mark.integration
@pytest.mark.django_db()
def test_picture_creation(sample_picture_model: PictureModel) -> None:
    # arrange
    picture = sample_picture_model

    # act
    picture.save()

    # assert
    assert picture.id is not None
    assert picture.display_order == 1
