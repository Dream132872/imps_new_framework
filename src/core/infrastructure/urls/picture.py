"""
Core picture urls.
"""

from django.urls import path, include
from core.infrastructure.views import picture


urlpatterns = [
    path(
        # admin views for auth
        "admin/picture/",
        include(
            (
                [
                    path(
                        "create/<str:content_type>/<str:object_id>/",
                        picture.CreatePictureView.as_view(),
                        name="create",
                    ),
                    path(
                        "create/<str:picture_id>/",
                        picture.UpdatePictureView.as_view(),
                        name="create",
                    ),
                ],
                "picture",
            ),
            namespace="picture",
        ),
    ),
]
