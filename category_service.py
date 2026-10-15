
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository
from app.models.product import Product


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)

    def _write(self, operation):
        try:
            result = operation()
            self.db.commit()
            return result
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "Category conflicts with existing data."
            ) from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise HTTPException(
                500, "Database operation failed."
            ) from exc

    def list(self, **kwargs):
        return self.repo.list(**kwargs)

    def get(self, category_id):
        obj = self.repo.get(category_id)
        if not obj:
            raise HTTPException(404, "Category not found.")
        return obj

    def create(self, data):
        values = data.model_dump()
        if self.repo.get_by_name(values["name"]):
            raise HTTPException(409, "Category name already exists.")
        return self._write(lambda: self.repo.create(values))

    def update(self, category_id, data):
        obj = self.get(category_id)
        values = data.model_dump(exclude_unset=True)

        if "name" in values and values["name"] != obj.name:
            if self.repo.get_by_name(values["name"]):
                raise HTTPException(409, "Category name already exists.")

        def operation():
            for key, value in values.items():
                setattr(obj, key, value)
            self.db.flush()
            return obj

        return self._write(operation)

    def delete(self, category_id):
        obj = self.get(category_id)
        if self.db.query(Product.id).filter(
            Product.category_id == category_id
        ).first():
            raise HTTPException(
                409, "Cannot delete a category assigned to products."
            )

        def operation():
            self.repo.delete(obj)
            return {"message": "Category deleted successfully."}

        return self._write(operation)
