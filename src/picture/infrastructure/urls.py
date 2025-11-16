"""
Picture urls.
"""

from django.urls import path, include
from picture.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
)
from core.infrastructure.views import chunk_upload


urlpatterns = [
    path(
        "admin/picture/",
        include(
            (
                [
                    path(
                        "create/<str:picture_type>/<str:content_type>/<str:object_id>/",
                        CreatePictureView.as_view(),
                        name="create",
                    ),
                    path(
                        "update/<str:picture_id>/",
                        UpdatePictureView.as_view(),
                        name="update",
                    ),
                    path(
                        "delete/<str:pk>/",
                        DeletePictureView.as_view(),
                        name="delete",
                    ),
                    path(
                        "chunk/create/",
                        chunk_upload.CreateChunkUploadView.as_view(),
                        name="chunk_create",
                    ),
                    path(
                        "chunk/upload/",
                        chunk_upload.UploadChunkView.as_view(),
                        name="chunk_upload",
                    ),
                    path(
                        "chunk/complete/",
                        chunk_upload.CompleteChunkUploadView.as_view(),
                        name="chunk_complete",
                    ),
                    path(
                        "chunk/status/<str:upload_id>/",
                        chunk_upload.GetChunkUploadStatusView.as_view(),
                        name="chunk_status",
                    ),
                ],
                "picture",
            ),
            namespace="picture",
        ),
    ),
]
