
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.supplier_repository import SupplierRepository


class SupplierService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SupplierRepository(db)

    def _write(self, operation):
        try:
            result = operation()
            self.db.commit()
            return result
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Supplier conflicts with existing data.") from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(500, "Database operation failed.") from exc

    def list(self, **kwargs):
        return self.repo.list(**kwargs)

    def get(self, supplier_id):
        obj = self.repo.get(supplier_id)
        if not obj:
            raise HTTPException(404, "Supplier not found.")
        return obj

    def create(self, data):
        values = data.model_dump()
        if self.repo.get_by_email(str(values["email"])):
            raise HTTPException(409, "Supplier email already exists.")
        return self._write(lambda: self.repo.create(values))

    def update(self, supplier_id, data):
        obj = self.get(supplier_id)
        values = data.model_dump(exclude_unset=True)

        if "email" in values and values["email"] is not None:
            email = str(values["email"])
            existing = self.repo.get_by_email(email)
            if existing and existing.id != supplier_id:
                raise HTTPException(409, "Supplier email already exists.")
            values["email"] = email

        # Prevent deactivating a supplier while its products reference it.
        if values.get("is_active") is False:
            has_products = self.db.scalar(
                select(Product.id).where(
                    Product.supplier_id == supplier_id
                ).limit(1)
            )
            if has_products:
                raise HTTPException(
                    409, "Cannot deactivate a supplier assigned to products."
                )

        def operation():
            for key, value in values.items():
                setattr(obj, key, value)
            self.db.flush()
            return obj

        return self._write(operation)

    def delete(self, supplier_id):
        obj = self.get(supplier_id)
        has_products = self.db.scalar(
            select(Product.id).where(
                Product.supplier_id == supplier_id
            ).limit(1)
        )
        if has_products:
            raise HTTPException(
                409, "Cannot delete a supplier assigned to products."
            )

        def operation():
            self.repo.delete(obj)
            return {"message": "Supplier deleted successfully."}

        return self._write(operation)
