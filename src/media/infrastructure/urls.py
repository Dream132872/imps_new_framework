"""
Media urls.
"""

from django.urls import path, include
from media.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
    CreateChunkUploadView,
    UploadChunkView,
    CompletePictureChunkUploadView,
    CompleteAttachmentChunkUploadView,
    GetChunkUploadStatusView,
    CreateAttachmentView,
    DeleteAttachmentView,
    UpdateAttachmentView,
)

app_name = "media"

picture_urlpatterns = [
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
]

attachment_urlpatterns = [
    path(
        "create/<str:content_type>/<str:object_id>/",
        CreateAttachmentView.as_view(),
        name="create",
    ),
    path(
        "update/<str:attachment_id>/",
        UpdateAttachmentView.as_view(),
        name="update",
    ),
    path(
        "delete/<str:pk>/",
        DeleteAttachmentView.as_view(),
        name="delete",
    ),
]

chunk_upload_urlpatterns = [
    path(
        "create/",
        CreateChunkUploadView.as_view(),
        name="create",
    ),
    path(
        "upload/",
        UploadChunkView.as_view(),
        name="upload",
    ),
    path(
        "complete/",
        CompletePictureChunkUploadView.as_view(),
        name="complete",
    ),
    path(
        "complete-attachment/",
        CompleteAttachmentChunkUploadView.as_view(),
        name="complete_attachment",
    ),
    path(
        "status/<str:upload_id>/",
        GetChunkUploadStatusView.as_view(),
        name="status",
    ),
]

urlpatterns = [
    path(
        "admin/media/",
        include(
            [
                path(
                    "picture/",
                    include(
                        (picture_urlpatterns, "picture"),
                        namespace="picture",
                    ),
                ),
                path(
                    "attachment/",
                    include(
                        (attachment_urlpatterns, "attachment"),
                        namespace="attachment",
                    ),
                ),
                path(
                    "chunk-upload/",
                    include(
                        (chunk_upload_urlpatterns, "chunk_upload"),
                        namespace="chunk_upload",
                    ),
                ),
            ],
        ),
    ),
]
