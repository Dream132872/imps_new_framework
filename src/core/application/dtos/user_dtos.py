"""
Data Transfer Objects for User
"""

import uuid
from typing import Optional
from datetime import datetime
from dataclasses import dataclass


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
