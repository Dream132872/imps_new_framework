"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import os

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    return JsonResponse({
        "status": "healthy",
        "workers": os.getenv("UVICORN_WORKERS", "12"),
        "concurrency_limit": os.getenv("UVICORN_LIMIT_CONCURRENCY", "300"),
        "gunicorn_workers": os.getenv("GUNICORN_WORKERS", "12"),
        "gunicorn_connections": os.getenv("GUNICORN_WORKER_CONNECTIONS", "1000"),
        "async_threads": os.getenv("ASYNC_THREADS", "16"),
    })

urlpatterns = [
    path("health/", health_check, name="health_check"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    path("admin-django/doc/", include("django.contrib.admindocs.urls")),
    path("admin-django/", admin.site.urls),
    path("", include("shared.infrastructure.urls")),
    path("", include("core.infrastructure.urls")),
    prefix_default_language=settings.MULTILANGUAGE_URL_PREFIX,
)
