import uuid

import pytest

from media.domain.entities.chunk_upload_entities import ChunkUploadStatus
from media.domain.exceptions import ChunkUploadNotFoundError
from media.infrastructure.repositories import DjangoChunkUploadRepository

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.infrastructure,
]


class TestDjangoChunkUploadRepository:
    def test_get_by_upload_id_supports_uuid_and_string(
        self, chunk_upload_entity_factory
    ) -> None:
        repo = DjangoChunkUploadRepository()
        upload_id = uuid.uuid4()
        entity = chunk_upload_entity_factory(
            upload_id=upload_id,
            total_size=5000,
            uploaded_size=2500,
            chunk_count=3,
            status=ChunkUploadStatus.UPLOADING,
        )

        saved = repo.save(entity)

        fetched_by_uuid = repo.get_by_upload_id(upload_id)
        fetched_by_string = repo.get_by_upload_id(str(upload_id))

        assert fetched_by_uuid.id == saved.id
        assert fetched_by_uuid.upload_id == str(upload_id)
        assert fetched_by_uuid.status == ChunkUploadStatus.UPLOADING.value

        assert fetched_by_string.id == saved.id
        assert fetched_by_string.upload_id == str(upload_id)

    def test_get_by_upload_id_raises_not_found(self) -> None:
        repo = DjangoChunkUploadRepository()

        with pytest.raises(ChunkUploadNotFoundError):
            repo.get_by_upload_id(uuid.uuid4())

