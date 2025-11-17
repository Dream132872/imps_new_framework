from django.urls import include, path


urlpatterns = [
    path(
        "",
        include(
            (
                [
                    path("", include("identity.infrastructure.urls.auth")),
                ],
                "identity",
            ),
            namespace="identity",
        ),
    ),
]

