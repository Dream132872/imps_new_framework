"""Test picture query handlers"""

from unittest.mock import MagicMock

import pytest
from django.contrib.contenttypes.models import ContentType

from media.application.dtos import PictureDTO
from media.application.queries.picture_queries import (
    GetPictureByIdQuery,
    SearchFirstPictureQuery,
    SearchPicturesQuery,
)
from media.application.query_handlers.picture_query_handlers import (
    SearchFirstPictureQueryHandler,
    SearchPicturesQueryHandler,
)
from media.domain.entities import Picture as PictureEntity
from media.domain.repositories import PictureRepository


@pytest.mark.application
@pytest.mark.unit
class TestSearchPicturesQueryHandler:
    """Test searching pictures"""

    def test_search_pictures_with_content_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching pictures"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_pictures.return_value = [
            sample_picture_entity
        ]

        query = SearchPicturesQuery(content_type_id=sample_content_type.id)
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0].id == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestSearchFirstPictureQueryHandler:
    """Test searching first occurrance of picture"""

    def test_search_first_picture_with_content_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first picture with special information"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_pictures.return_value = [
            sample_picture_entity
        ]

        query = SearchFirstPictureQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert result.id == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once()
