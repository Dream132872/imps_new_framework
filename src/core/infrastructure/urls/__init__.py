from django.urls import include, path


urlpatterns = [
    path(
        "",
        include(
            (
                [
                    path("", include("core.infrastructure.urls.base")),
                    path("", include("core.infrastructure.urls.auth")),
                    path("", include("core.infrastructure.urls.picture")),
                ],
                "core",
            ),
            namespace="core",
        ),
    ),
]
