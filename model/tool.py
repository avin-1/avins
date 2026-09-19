from pydantic import BaseModel, Field


class Tool(BaseModel):
    name: str = ""
    message: list[str] = Field(default_factory=list)


__all__ = ["Tool"]
