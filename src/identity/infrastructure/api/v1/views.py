"""
Identity api views version 1.
"""

from asgiref.sync import sync_to_async
from ninja_extra import api_controller, route
from ninja_jwt.controller import AsyncTokenObtainPairController

from identity.infrastructure.api.v1.schemas import (
    CustomTokenObtainPairInputSchema,
    CustomTokenObtainPairOutputSchema,
    CustomTokenRefreshInputSchema,
    CustomTokenRefreshOutputSchema,
)


@api_controller("token/", tags=["Auth"])
class CustomTokenObtainPairController(AsyncTokenObtainPairController):
    @route.post(
        "pair/",
        response=CustomTokenObtainPairOutputSchema,
        url_name="token_obtain_pair",
    )
    async def obtain_token(self, user_token: CustomTokenObtainPairInputSchema):
        """Generate Access and Referesh Tokens for authentication."""

        await sync_to_async(user_token.check_user_authentication_rule)()
        return user_token.output_schema()

    @route.post(
        "refresh/",
        response=CustomTokenRefreshOutputSchema,
        url_name="token_refresh",
        operation_id="token_refresh",
    )
    async def refresh_token(self, refresh_token: CustomTokenRefreshInputSchema):
        """Re-Validate Access token via Referesh token."""

        return await super().refresh_token(refresh_token)
