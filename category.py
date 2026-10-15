
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import ORMBase


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class CategoryOut(ORMBase):
    id: int
    name: str
    description: str | None
