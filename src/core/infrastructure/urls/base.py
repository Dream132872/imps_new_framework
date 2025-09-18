from django.urls import path
from ..views import base


urlpatterns = [
    path("admin/", base.HomeView.as_view(), name="index_view"),
]
