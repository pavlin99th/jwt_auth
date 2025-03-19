import logging
from json import JSONDecodeError

from async_fastapi_jwt_auth import AuthJWT  # type: ignore
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer  # type: ignore
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from httpx import AsyncClient, HTTPError, HTTPStatusError

from config import Settings, settings


@AuthJWT.load_config  # type: ignore
def get_config() -> Settings:
    """Provide config to jwt module."""
    return settings


class AuthValidator:
    """
    Authorize user based on token roles.
    This validator checks if the required roles are present in the token.
    Performs an additional request to a remote
    authentication service to check for access token revocation (after logout).
    """

    auth_url = str(settings.authjwt_validator)
    client = AsyncClient()

    def __init__(self, required_roles: set[str] = set()):
        """Initialize the validator with the required roles."""
        self.required_roles = required_roles

    async def __call__(
        self,
        request: Request,
        authorize: AuthJWT = Depends(AuthJWTBearer()),
    ) -> None:
        """Authorize the request by checking the presence of required roles."""
        await authorize.jwt_required()

        if not self.required_roles:
            return
        token = await authorize.get_raw_jwt()
        roles_in_token = set(token.get("roles", []))
        if not roles_in_token & self.required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        auth = request.headers.get("Authorization", "")
        try:
            resp = await self.client.get(self.auth_url, headers={"Authorization": auth})
        except HTTPError as err:
            logging.error("Remote auth service communication failed: %r", err)
            return

        try:
            resp.raise_for_status()
        except HTTPStatusError:
            if resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                logging.error("Remote auth service internal error")
                return
            try:
                detail = resp.json()["detail"]
            except (UnicodeDecodeError, JSONDecodeError, KeyError) as err:
                logging.error("Remote auth validation malformed response: %r", err)
                detail = None
            raise HTTPException(status_code=resp.status_code, detail=detail)
