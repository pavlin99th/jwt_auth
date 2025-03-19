from fastapi import APIRouter, Depends

from jwt_auth import AuthValidator
from models import Content

content = APIRouter(tags=["Content"])


@content.get(
    "/content_1",
    dependencies=[Depends(AuthValidator({"role1"}))],
)
async def get_content1() -> Content:
    """Get dummy content 1 (role1)."""
    return Content(data="Content 1, available only to users with role1.")


@content.get(
    "/content_2",
    dependencies=[Depends(AuthValidator({"role1", "role2"}))],
)
async def get_content2() -> Content:
    """Get dummy content 2 (role1 or role2)."""
    return Content(data="Content 2, available only to users with role1 and/or role2.")
