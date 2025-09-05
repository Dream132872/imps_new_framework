from django.urls import include, path


urlpatterns = [
    path("", include(("core.infrastructure.urls.base", "core"), namespace="core"))
]
