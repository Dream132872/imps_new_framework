"""
Data Transfer Objects for User
"""

import uuid
from dataclasses import dataclass
from datetime import datetime

__all__ = ("UserDTO",)


@dataclass
class UserDTO:
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
