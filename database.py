
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.category_service import CategoryService
from app.services.supplier_service import SupplierService
from app.services.product_service import ProductService

DBSession = Annotated[Session, Depends(get_db)]


def get_category_service(db: DBSession) -> CategoryService:
    return CategoryService(db)


def get_supplier_service(db: DBSession) -> SupplierService:
    return SupplierService(db)


def get_product_service(db: DBSession) -> ProductService:
    return ProductService(db)


CategoryServiceDep = Annotated[
    CategoryService, Depends(get_category_service)
]
SupplierServiceDep = Annotated[
    SupplierService, Depends(get_supplier_service)
]
ProductServiceDep = Annotated[
    ProductService, Depends(get_product_service)
]
