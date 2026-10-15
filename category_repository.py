
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, category_id: int):
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str):
        return self.db.scalar(
            select(Category).where(Category.name == name)
        )

    def list(self, skip=0, limit=100, search=None):
        stmt = select(Category)
        if search:
            stmt = stmt.where(Category.name.ilike(f"%{search}%"))
        return list(
            self.db.scalars(stmt.order_by(Category.id).offset(skip).limit(limit))
        )

    def create(self, data):
        obj = Category(**data)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.flush()
