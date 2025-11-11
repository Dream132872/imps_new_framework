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

import os

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from django.utils import timezone
from django.views.decorators.http import last_modified, require_http_methods
from django.views.i18n import JavaScriptCatalog
from django_js_reverse.views import urls_js as django_js_url_reverse

last_modified_date = timezone.now()


@require_http_methods(["GET"])
def health_check(request: HttpRequest) -> JsonResponse:
    """Health check endpoint for monitoring and load balancers."""
    return JsonResponse(
        {
            "status": "healthy",
            "workers": os.getenv("UVICORN_WORKERS", "12"),
            "concurrency_limit": os.getenv("UVICORN_LIMIT_CONCURRENCY", "300"),
            "gunicorn_workers": os.getenv("GUNICORN_WORKERS", "12"),
            "gunicorn_connections": os.getenv("GUNICORN_WORKER_CONNECTIONS", "1000"),
            "async_threads": os.getenv("ASYNC_THREADS", "16"),
        }
    )


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("admin-django/rosetta/", include("rosetta.urls")),
    path("urls-js/", django_js_url_reverse, name="django_js_url_reverse"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += i18n_patterns(
    path("admin-django/doc/", include("django.contrib.admindocs.urls")),
    path("admin-django/", admin.site.urls),
    path(
        "jsi18n/",
        last_modified(lambda req, **kw: last_modified_date)(
            JavaScriptCatalog.as_view()
        ),
        name="javascript-catalog",
    ),
    path("", include("shared.infrastructure.urls")),
    path("", include("core.infrastructure.urls")),
    prefix_default_language=settings.MULTILANGUAGE_URL_PREFIX,
)


if settings.DEBUG and not settings.TESTING:
    urlpatterns += debug_toolbar_urls()
