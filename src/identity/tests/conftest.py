import pytest

from identity.infrastructure.models import User


@pytest.fixture
def identity_admin_user(db):
    return User.objects.create_superuser(
        username="admin_user", email="admin@admin.com", password="123"
    )
