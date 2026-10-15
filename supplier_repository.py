
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, supplier_id: int):
        return self.db.get(Supplier, supplier_id)

    def get_by_email(self, email: str):
        return self.db.scalar(
            select(Supplier).where(Supplier.email == email)
        )

    def list(self, skip=0, limit=100, search=None, active=None):
        stmt = select(Supplier)
        if search:
            stmt = stmt.where(Supplier.name.ilike(f"%{search}%"))
        if active is not None:
            stmt = stmt.where(Supplier.is_active == active)
        return list(
            self.db.scalars(stmt.order_by(Supplier.id).offset(skip).limit(limit))
        )

    def create(self, data):
        obj = Supplier(**data)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.flush()
