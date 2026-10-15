
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.supplier_repository import SupplierRepository


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.categories = CategoryRepository(db)
        self.suppliers = SupplierRepository(db)

    def _write(self, operation):
        try:
            result = operation()
            self.db.commit()
            return result
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "Database conflict: check SKU and related records."
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(500, "Database operation failed.") from exc

    def _validate_relations(self, values):
        if "category_id" in values:
            if self.categories.get(values["category_id"]) is None:
                raise HTTPException(404, "Category not found.")

        if "supplier_id" in values:
            supplier = self.suppliers.get(values["supplier_id"])
            if supplier is None:
                raise HTTPException(404, "Supplier not found.")
            if not supplier.is_active:
                raise HTTPException(
                    409, "Inactive suppliers cannot be assigned to products."
                )

    def list(self, **kwargs):
        return self.repo.list(**kwargs)

    def get(self, product_id):
        obj = self.repo.get(product_id)
        if obj is None:
            raise HTTPException(404, "Product not found.")
        return obj

    def create(self, data):
        values = data.model_dump()
        if self.repo.get_by_sku(values["sku"]):
            raise HTTPException(409, "Product SKU already exists.")

        self._validate_relations(values)
        return self._write(lambda: self.repo.create(values))

    def update(self, product_id, data):
        obj = self.get(product_id)
        values = data.model_dump(exclude_unset=True)

        if "sku" in values and values["sku"] != obj.sku:
            if self.repo.get_by_sku(values["sku"]):
                raise HTTPException(409, "Product SKU already exists.")

        self._validate_relations(values)

        def operation():
            for key, value in values.items():
                setattr(obj, key, value)
            self.db.flush()
            return obj

        return self._write(operation)

    def delete(self, product_id):
        obj = self.get(product_id)

        def operation():
            self.repo.delete(obj)
            return {"message": "Product deleted successfully."}

        return self._write(operation)
