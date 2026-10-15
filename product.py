
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import ORMBase


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    sku: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    category_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    sku: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)


class ProductOut(ORMBase):
    id: int
    name: str
    sku: str
    description: str | None
    price: Decimal
    quantity: int
    reorder_level: int
    category_id: int
    supplier_id: int
