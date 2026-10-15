
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import engine
from app.routers import category, supplier, product


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic owns schema creation and updates.
    yield
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description=(
        "Inventory API using FastAPI, SQLAlchemy, MySQL, "
        "Pydantic, Alembic, repositories and services."
    ),
    lifespan=lifespan,
)

app.include_router(category.router)
app.include_router(supplier.router)
app.include_router(product.router)


@app.get("/", tags=["Health"], summary="API health information")
def root():
    return {
        "message": "Inventory Management API is running",
        "docs": "/docs",
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"], summary="Check database connectivity")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "unavailable",
            },
        )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    # Log the exception server-side in production; do not return its details.
    if settings.debug:
        # Do not expose exception strings even in debug API responses.
        pass
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )
