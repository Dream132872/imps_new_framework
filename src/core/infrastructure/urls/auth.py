from django.urls import path, include
from ..views import auth


urlpatterns = [
    path(
        # admin views for auth
        "admin/auth/",
        include(
            (
                [
                    path("login/", auth.LoginView.as_view(), name="login_view"),
                ],
                "auth",
            ),
            namespace="auth",
        ),
    ),
]
