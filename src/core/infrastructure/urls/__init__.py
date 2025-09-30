from django.urls import include, path


urlpatterns = [
    path("", include(("core.infrastructure.urls.base", "core"), namespace="core")),
    path("", include(("core.infrastructure.urls.auth", "core"), namespace="core")),
]
