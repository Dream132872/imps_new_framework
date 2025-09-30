from django.urls import path, include
from ..views import base


urlpatterns = [
    path(
        # admin views for base
        "admin/",
        include(
            (
                [
                    path("", base.HomeView.as_view(), name="home"),
                ],
                "base",
            ),
            namespace="base",
        ),
    ),
    path("api/users/", base.SampleApiView.as_view(), name="users_view"),
]
