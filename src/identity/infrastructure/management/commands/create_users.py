import uuid
from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        from ...models import User

        for i in range(500):
            User.objects.create_superuser(
                username=str(uuid.uuid4()), password="test", email=""
            )
