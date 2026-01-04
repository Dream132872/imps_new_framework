"""Implement custom auth backend that would work with django-guardian package"""

from typing import Any

from django.contrib.contenttypes.models import ContentType
from guardian.backends import ObjectPermissionBackend

from identity.infrastructure.models import User


class ExclusionAwareObjectPermissionBackend(ObjectPermissionBackend):
    """
    Custom permission backend that checks exclusions after guardian checks.
    """

    def has_perm(self, user_obj: User, perm: str, obj: Any = None) -> bool:
        """
        Check permission, but exclude if object is in exclusion list.
        """
        # First check guardian's permission
        has_guardian_perm = super().has_perm(user_obj, perm, obj)

        if not has_guardian_perm:
            return False

        # # If guardian says yes, check exclusions
        # if obj is not None:
        #     from shared.infrastructure.models.permission_exclusion import (
        #         PermissionExclusion,
        #     )

        #     content_type = ContentType.objects.get_for_model(obj)
        #     is_excluded = PermissionExclusion.objects.filter(
        #         user=user_obj,
        #         permission=perm.split(".")[-1],  # Get codename from 'app.codename'
        #         content_type=content_type,
        #         object_id=obj.pk,
        #     ).exists()

        #     if is_excluded:
        #         return False

        return has_guardian_perm
