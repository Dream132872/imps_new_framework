import pytest
from pytest_django.fixtures import SettingsWrapper

from media.infrastructure.models.picture import Picture


def test_sum(settings: SettingsWrapper):
    print("testing: ", settings.TESTING)
    print("hello")
    assert 1 + 2 == 3


# @pytest.mark.integration
@pytest.mark.django_db
class TestPicture:
    @pytest.fixture(scope="class", autouse=True)
    def sample_picture(self):
        pic = Picture.objects.create(
            image="images/test.png",
            alternative="alt message",
            title="title of image",
            content_type_id=1,
            object_id="1",
            picture_type="main",
        )

        yield pic

        pic.delete()

    def test_get_pictures(self):

        assert (
            len(list(Picture.objects.all())) == 1
        ), "We have no picture in database. but it shows atleast one."

        with pytest.raises(Picture.DoesNotExist) as exc_info:
            Picture.objects.get(image="test.png")

    def test_request_first_page(self):
        pass
