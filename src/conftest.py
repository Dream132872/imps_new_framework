"""Global conftest for entire project."""

import copy
import logging
from typing import Any, Generator

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache, caches
from pytest_django.fixtures import SettingsWrapper

logger = logging.getLogger(__file__)


@pytest.fixture(autouse=True)
def change_default_cache_location(
    settings: SettingsWrapper,
) -> Generator[None, Any, None]:
    """
    Overrides the default cache location for all tests.
    redis db would be clear after each test run.
    """

    # manage default cache
    copied_default_cache = copy.deepcopy(settings.CACHES["default"])
    copied_default_cache["LOCATION"] = "redis://localhost:6379/10"
    settings.CACHES["default"] = copied_default_cache

    # manage sessions cache
    copied_sessions_cache = copy.deepcopy(settings.CACHES["sessions"])
    copied_sessions_cache["LOCATION"] = "redis://localhost:6379/11"
    settings.CACHES["sessions"] = copied_sessions_cache
    yield
    # clear all caches from default and sessions
    cache.clear()
    caches["sessions"].clear()


@pytest.fixture
def sample_content_type(db: None) -> ContentType:
    content_type = ContentType.objects.get_for_model(ContentType)
    return content_type
