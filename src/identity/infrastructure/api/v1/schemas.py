"""
Identity schemas.
"""

import uuid

from ninja import Schema
from ninja_jwt.schema import (
    TokenObtainPairInputSchema,
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
)


class UserSchema(Schema):
    """User information schema."""

    id: str | uuid.UUID
    username: str
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    is_staff: bool
    is_superuser: bool
    is_active: bool


class CustomTokenObtainPairOutputSchema(Schema):
    """Output schema of JWT login."""

    access: str
    refresh: str
    user: UserSchema


class CustomTokenObtainPairInputSchema(TokenObtainPairInputSchema):
    """Input schema of JWT login."""

    def output_schema(self):
        out_dict = self.get_response_schema_init_kwargs()
        out_dict.update(user=UserSchema.from_orm(self._user))
        return CustomTokenObtainPairOutputSchema(**out_dict)


class CustomTokenRefreshInputSchema(TokenRefreshInputSchema):
    pass


class CustomTokenRefreshOutputSchema(TokenRefreshOutputSchema):
    pass
