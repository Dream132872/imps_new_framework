"""
Chunk Upload Queries for CQRS implementation (moved from core bounded context).
"""

from dataclasses import dataclass

from shared.application.cqrs import Query

__all__ = ("GetChunkUploadStatusQuery",)


@dataclass
class GetChunkUploadStatusQuery(Query):
    upload_id: str


