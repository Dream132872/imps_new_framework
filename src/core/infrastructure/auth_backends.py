from typing import Any

from adrf.mixins import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.cache import cache


class CachedModelBackend(ModelBackend):
    """Authentication backend that caches user objects."""

    async def aget_user(self, user_id: int) -> AbstractBaseUser | None:
        return await sync_to_async(self.get_user)(user_id)

    def get_user(self, user_id: Any):
        """Get user from cache first, then from database."""
        cache_key = f"user:{user_id}"
        user = cache.get(cache_key)

        if user is None:
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id)
                # Cache for 5 minutes
                cache.set(cache_key, user, 300)
            except User.DoesNotExist:
                return None

        return user if user.is_active else None
