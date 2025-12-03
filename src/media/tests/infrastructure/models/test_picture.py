"""Test picture model."""

import uuid
from unittest.mock import MagicMock, call, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from media.infrastructure.models.picture import Picture as PictureModel


@pytest.mark.infrastructure
@pytest.mark.slow
@pytest.mark.unit
def test_picture_items(
    sample_picture_model: PictureModel, mock_picture_repository: MagicMock
):
    assert sample_picture_model.title == "title"


@pytest.mark.unit
def test_mocking():
    mock = MagicMock()

    mock.method("first")
    mock.method("second")
    mock.method("third")

    # Check call count
    assert mock.method.call_count == 3

    # Check all calls
    assert mock.method.call_args_list == [
        call("first"),
        call("second"),
        call("third"),
    ]

    # Check last call
    assert mock.method.call_args == call("third")


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
