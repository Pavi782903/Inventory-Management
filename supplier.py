
from pydantic import BaseModel, Field, EmailStr
from app.schemas.common import ORMBase


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    is_active: bool = True


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    is_active: bool | None = None


class SupplierOut(ORMBase):
    id: int
    name: str
    email: str
    phone: str | None
    address: str | None
    is_active: bool
