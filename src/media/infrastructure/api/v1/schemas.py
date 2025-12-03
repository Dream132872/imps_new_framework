"""
Picture related schemas.
"""

import uuid

from ninja import Schema


class User(Schema):
    id: str | uuid.UUID
    username: str
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    is_staff: bool
    is_superuser: bool
    is_active: bool
