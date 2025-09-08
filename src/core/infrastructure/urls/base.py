from django.urls import path
from ..views import base


urlpatterns = [
    path("admin/", base.HomeView.as_view(), name="index_view"),
    path("api/todos/", base.TodosApiView.as_view()),
]
