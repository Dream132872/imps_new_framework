from django.urls import path
from ..views import base


urlpatterns = [
    path("admin/", base.HomeView.as_view(), name="index_view"),
    path("admin/<uuid:pk>", base.HomeView.as_view(), name="index_view"),
    path("api/users/", base.SampleApiView.as_view(), name="users_view"),
]
