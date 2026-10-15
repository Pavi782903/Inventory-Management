
import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Configure a dedicated test database URL before importing the app.
if not os.getenv("TEST_DATABASE_URL"):
    pytest.skip(
        "Set TEST_DATABASE_URL to a dedicated MySQL test database.",
        allow_module_level=True,
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.connection import get_db
from app.main import app
from app.models import Category, Supplier, Product


@pytest.fixture()
def client():
    # The test URL must point to a dedicated disposable database.
    engine = create_engine(
        os.environ["TEST_DATABASE_URL"],
        pool_pre_ping=True,
    )
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    # Tests create only the tables declared by the application models.
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_product_crud_and_duplicate_sku(client):
    suffix = uuid.uuid4().hex[:10]

    category = client.post(
        "/categories/",
        json={"name": f"Test-{suffix}", "description": "Test category"},
    )
    assert category.status_code == 201, category.text
    category_id = category.json()["id"]

    supplier = client.post(
        "/suppliers/",
        json={
            "name": f"Supplier-{suffix}",
            "email": f"{suffix}@example.com",
            "is_active": True,
        },
    )
    assert supplier.status_code == 201, supplier.text
    supplier_id = supplier.json()["id"]

    payload = {
        "name": "Test Product",
        "sku": f"SKU-{suffix}",
        "price": "25.50",
        "quantity": 5,
        "reorder_level": 5,
        "category_id": category_id,
        "supplier_id": supplier_id,
    }

    created = client.post("/products/", json=payload)
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    duplicate = client.post("/products/", json=payload)
    assert duplicate.status_code == 409

    fetched = client.get(f"/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json()["sku"] == payload["sku"]

    restock = client.get("/products/?needs_restock=true")
    assert restock.status_code == 200
    assert any(p["id"] == product_id for p in restock.json())

    updated = client.put(
        f"/products/{product_id}", json={"quantity": 20}
    )
    assert updated.status_code == 200
    assert updated.json()["quantity"] == 20

    deleted = client.delete(f"/products/{product_id}")
    assert deleted.status_code == 200

    missing = client.get(f"/products/{product_id}")
    assert missing.status_code == 404


def test_invalid_product_quantity(client):
    response = client.post(
        "/products/",
        json={
            "name": "Invalid Product",
            "sku": "INVALID-001",
            "price": "10.00",
            "quantity": -1,
            "reorder_level": 5,
            "category_id": 1,
            "supplier_id": 1,
        },
    )
    assert response.status_code == 422
