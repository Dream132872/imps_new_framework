import pytest


def test_sum():
    assert 1 + 2 == 3


@pytest.mark.django_db
def test_get_users():
    from media.infrastructure.models.picture import Picture

    assert len(list(Picture.objects.all())) == 0
