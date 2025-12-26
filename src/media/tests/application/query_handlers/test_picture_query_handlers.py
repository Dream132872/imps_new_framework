"""Test picture query handlers"""

import uuid
from typing import Callable
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
    GetPictureByIdQueryHandler,
    SearchFirstPictureQueryHandler,
    SearchPicturesQueryHandler,
)
from media.domain.entities import Picture as PictureEntity
from media.domain.entities.picture_entities import PictureType
from media.domain.exceptions import PictureNotFoundError
from media.domain.repositories import PictureRepository
from shared.application.exceptions import ApplicationError, ApplicationNotFoundError


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
        assert str(result[0].id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            picture_type="main",
        )

    def test_search_pictures_with_all_parameters(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
        sample_content_type: ContentType,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test searching pictures with all query parameters"""

        # Arrange
        object_id = str(uuid.uuid4())
        picture_type = PictureType.GALLERY.value
        picture1 = sample_picture_entity
        picture2 = picture_entity_factory(
            picture_object_id=object_id,
            picture_type=picture_type,
        )

        mock_unit_of_work[PictureRepository].search_pictures.return_value = [
            picture1,
            picture2,
        ]

        query = SearchPicturesQuery(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            picture_type=picture_type,
        )
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 2
        assert str(result[0].id) == picture1.id
        assert str(result[1].id) == picture2.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=object_id,
            picture_type=picture_type,
        )

    def test_search_pictures_returns_empty_list(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching pictures when no results found"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_pictures.return_value = []

        query = SearchPicturesQuery(content_type_id=sample_content_type.id)
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 0
        assert isinstance(result, list)

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            picture_type="main",
        )

    def test_search_pictures_with_only_object_id(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test searching pictures with only object_id parameter"""

        # Arrange
        object_id = str(uuid.uuid4())
        mock_unit_of_work[PictureRepository].search_pictures.return_value = [
            sample_picture_entity
        ]

        query = SearchPicturesQuery(object_id=object_id)
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert str(result[0].id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once_with(
            content_type=None,
            object_id=object_id,
            picture_type="main",
        )

    def test_search_pictures_with_only_picture_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test searching pictures with only picture_type parameter"""

        # Arrange
        picture_type = PictureType.AVATAR.value
        mock_unit_of_work[PictureRepository].search_pictures.return_value = [
            sample_picture_entity
        ]

        query = SearchPicturesQuery(picture_type=picture_type)
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert str(result[0].id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_pictures.assert_called_once_with(
            content_type=None,
            object_id=None,
            picture_type=picture_type,
        )

    def test_search_pictures_when_repository_raises_error(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test searching pictures when repository raises error"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_pictures.side_effect = Exception(
            "Database error"
        )

        query = SearchPicturesQuery(content_type_id=sample_content_type.id)
        handler = SearchPicturesQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            handler.handle(query)

        assert "Database error" in str(exc_info.value)

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
        mock_unit_of_work[PictureRepository].search_first_picture.return_value = sample_picture_entity

        query = SearchFirstPictureQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            picture_type="main",
        )

    def test_search_first_picture_with_all_parameters(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first picture with all query parameters"""

        # Arrange
        object_id = str(uuid.uuid4())
        picture_type = PictureType.BANNER.value

        mock_unit_of_work[PictureRepository].search_first_picture.return_value = (
            sample_picture_entity
        )

        query = SearchFirstPictureQuery(
            content_type_id=sample_content_type.id,
            object_id=object_id,
            picture_type=picture_type,
        )
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=object_id,
            picture_type=picture_type,
        )

    def test_search_first_picture_returns_none_when_not_found(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first picture when no picture found"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_first_picture.return_value = None

        query = SearchFirstPictureQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is None

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once_with(
            content_type=sample_content_type.id,
            object_id=None,
            picture_type="main",
        )

    def test_search_first_picture_with_only_object_id(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test finding first picture with only object_id parameter"""

        # Arrange
        object_id = str(uuid.uuid4())
        mock_unit_of_work[PictureRepository].search_first_picture.return_value = (
            sample_picture_entity
        )

        query = SearchFirstPictureQuery(object_id=object_id)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once_with(
            content_type=None,
            object_id=object_id,
            picture_type="main",
        )

    def test_search_first_picture_with_only_picture_type(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test finding first picture with only picture_type parameter"""

        # Arrange
        picture_type = PictureType.AVATAR.value
        mock_unit_of_work[PictureRepository].search_first_picture.return_value = (
            sample_picture_entity
        )

        query = SearchFirstPictureQuery(picture_type=picture_type)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once_with(
            content_type=None,
            object_id=None,
            picture_type=picture_type,
        )

    def test_search_first_picture_when_repository_raises_error(
        self,
        mock_unit_of_work: MagicMock,
        sample_content_type: ContentType,
    ) -> None:
        """Test finding first picture when repository raises error"""

        # Arrange
        mock_unit_of_work[PictureRepository].search_first_picture.side_effect = (
            Exception("Database error")
        )

        query = SearchFirstPictureQuery(content_type_id=sample_content_type.id)
        handler = SearchFirstPictureQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            handler.handle(query)

        assert "Database error" in str(exc_info.value)

        # Verify method calls
        mock_unit_of_work[PictureRepository].search_first_picture.assert_called_once()


@pytest.mark.application
@pytest.mark.unit
class TestGetPictureByIdQueryHandler:
    """Test getting picture by ID"""

    def test_get_picture_by_id_success(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
    ) -> None:
        """Test successfully getting picture by ID"""

        # Arrange
        picture_id = sample_picture_entity.id
        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )

        query = GetPictureByIdQuery(picture_id=picture_id)
        handler = GetPictureByIdQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id
        assert result.title == sample_picture_entity.title
        assert result.alternative == sample_picture_entity.alternative
        assert result.content_type_id == sample_picture_entity.content_type_id
        assert result.object_id == sample_picture_entity.object_id
        assert result.picture_type == sample_picture_entity.picture_type

        # Verify method calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            picture_id
        )

    def test_get_picture_by_id_when_not_found(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting picture by ID when picture not found"""

        # Arrange
        picture_id = str(uuid.uuid4())
        mock_unit_of_work[PictureRepository].get_by_id.side_effect = (
            PictureNotFoundError()
        )

        query = GetPictureByIdQuery(picture_id=picture_id)
        handler = GetPictureByIdQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationNotFoundError):
            handler.handle(query)

        # Verify method calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            picture_id
        )

    def test_get_picture_by_id_when_repository_raises_generic_error(
        self,
        mock_unit_of_work: MagicMock,
    ) -> None:
        """Test getting picture by ID when repository raises generic error"""

        # Arrange
        picture_id = str(uuid.uuid4())
        mock_unit_of_work[PictureRepository].get_by_id.side_effect = Exception(
            "Database connection error"
        )

        query = GetPictureByIdQuery(picture_id=picture_id)
        handler = GetPictureByIdQueryHandler(uow=mock_unit_of_work)

        # Act & Assert
        with pytest.raises(ApplicationError) as exc_info:
            handler.handle(query)

        assert picture_id in str(exc_info.value)

        # Verify method calls
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            picture_id
        )

    def test_get_picture_by_id_with_different_id_formats(
        self,
        mock_unit_of_work: MagicMock,
        sample_picture_entity: PictureEntity,
        picture_entity_factory: Callable[..., PictureEntity],
    ) -> None:
        """Test getting picture by ID with different ID formats"""

        # Arrange - Test with UUID string
        picture_id = str(uuid.uuid4())
        mock_unit_of_work[PictureRepository].get_by_id.return_value = (
            sample_picture_entity
        )

        query = GetPictureByIdQuery(picture_id=picture_id)
        handler = GetPictureByIdQueryHandler(uow=mock_unit_of_work)

        # Act
        result = handler.handle(query)

        # Assert
        assert result is not None
        assert str(result.id) == sample_picture_entity.id

        # Verify method calls - handler converts picture_id to string
        mock_unit_of_work[PictureRepository].get_by_id.assert_called_once_with(
            picture_id
        )
