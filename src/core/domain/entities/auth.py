import datetime
from typing import Any, Optional

from django.contrib.auth.hashers import make_password

from shared.domain.entities import AggregateRoot, ValueObject
from shared.domain.exceptions import ValidationError

__all__ = ("User", "Email")


class Email(ValueObject):
    """
    Email value object.
    """

    def __init__(self, value: str) -> None:
        if not self._is_valid_email(value):
            raise ValidationError("Invalid email format")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _get_equality_components(self) -> tuple:
        return (self._value,)

    def to_dict(self) -> dict[str, Any]:
        return {"email": self.value}


class User(AggregateRoot):
    def __init__(
        self,
        username: str,
        password: str,
        last_name: Optional[str] = "",
        first_name: Optional[str] = "",
        email: Optional[str] = "",
        is_staff: bool = False,
        is_superuser: bool = False,
        is_active: bool = True,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        id: Optional[str] = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._username = username
        self._first_name = first_name or ""
        self._last_name = last_name or ""
        self._email = Email(email) if email else None
        self._is_staff = is_staff
        self._is_superuser = is_superuser
        self._is_active = is_active
        self._password = password

    @property
    def username(self) -> str:
        return self._username

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self) -> str:
        return self.full_name if self.full_name else self.username

    @property
    def email(self) -> Optional[Email]:
        return self._email

    @property
    def is_staff(self) -> bool:
        return self._is_staff

    @property
    def is_superuser(self) -> bool:
        return self._is_superuser

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def password(self) -> str:
        return self._password

    def change_password(self, password: str) -> None:
        """Update user password."""
        self._password = make_password(password=password)
        self.update_timestamp()

    def promote_to_staff(self) -> None:
        """Promote user to staff member."""
        self._is_staff = True
        self.update_timestamp()

    def demote_from_staff(self) -> None:
        """Remove staff previllages from user."""
        self._is_staff = False
        self.update_timestamp()

    def promote_to_superuser(self) -> None:
        """Promote user to superuser."""
        self._is_staff = True
        self._is_superuser = True
        self.update_timestamp()

    def demote_from_superuser(self) -> None:
        """Remove superuser previllages from user."""
        self._is_superuser = True
        self.update_timestamp()

    def activate(self) -> None:
        """Activate user."""
        self._is_active = True
        self.update_timestamp()

    def deactivate(self) -> None:
        """Deactivate user."""
        self._is_active = False
        self.update_timestamp()

    def update_profile(
        self, first_name: str = "", last_name: str = "", email: Optional[Email] = None
    ) -> None:
        """Update user profile information."""
        if first_name:
            self._first_name = first_name

        if last_name:
            self._last_name = last_name

        if email:
            self._email = email

        self.update_timestamp()

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "username": self.username,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "full_name": self.full_name,
                "display_name": self.display_name,
                "email": self.email.value if self.email else "",
                "is_active": self.is_active,
                "is_staff": self.is_staff,
                "is_superuser": self.is_superuser,
            }
        )
        return base_dict
