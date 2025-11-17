from django.urls import path, include
from ..views import auth


urlpatterns = [
    path(
        # admin views for auth
        "admin/identity/",
        include(
            (
                [
                    path("login/", auth.LoginView.as_view(), name="login"),
                    path("logout/", auth.LogoutView.as_view(), name="logout"),
                ],
                "auth",
            ),
            namespace="auth",
        ),
    ),
]

