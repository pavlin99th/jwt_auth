from pydantic import BaseModel


class Content(BaseModel):
    """Describe dummy content model."""

    data: str
