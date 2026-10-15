
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int):
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str):
        return self.db.scalar(select(Product).where(Product.sku == sku))

    def list(
        self, skip=0, limit=100, search=None,
        category_id=None, supplier_id=None, needs_restock=None
    ):
        stmt = select(Product)

        if search:
            term = f"%{search}%"
            stmt = stmt.where(
                or_(Product.name.ilike(term), Product.sku.ilike(term))
            )
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if supplier_id is not None:
            stmt = stmt.where(Product.supplier_id == supplier_id)
        if needs_restock is True:
            stmt = stmt.where(Product.quantity <= Product.reorder_level)
        elif needs_restock is False:
            stmt = stmt.where(Product.quantity > Product.reorder_level)

        stmt = stmt.order_by(Product.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def create(self, data):
        obj = Product(**data)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.flush()
