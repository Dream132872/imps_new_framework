"""
Picture urls.
"""

from django.urls import path, include
from picture.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
)
from chunk_upload.infrastructure import views as chunk_upload_views


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
                        chunk_upload_views.CreateChunkUploadView.as_view(),
                        name="chunk_create",
                    ),
                    path(
                        "chunk/upload/",
                        chunk_upload_views.UploadChunkView.as_view(),
                        name="chunk_upload",
                    ),
                    path(
                        "chunk/complete/",
                        chunk_upload_views.CompleteChunkUploadView.as_view(),
                        name="chunk_complete",
                    ),
                    path(
                        "chunk/status/<str:upload_id>/",
                        chunk_upload_views.GetChunkUploadStatusView.as_view(),
                        name="chunk_status",
                    ),
                ],
                "picture",
            ),
            namespace="picture",
        ),
    ),
]
