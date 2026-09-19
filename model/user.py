from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    message: Optional[str] = None
    last_messages: list[dict] = Field(default_factory=list)


__all__ = ["User"]

