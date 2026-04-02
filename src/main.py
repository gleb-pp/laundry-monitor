from fastapi import FastAPI
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import src.routers.machines
from src.get_db import create_tables, create_initial_machines


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create database tables on application startup."""
    create_tables()
    create_initial_machines()
    yield

app = FastAPI(
    title="Laundry Monitor",
    description="A monitoring system for laundry machines in a dormitory.",
    version="1.0",
    lifespan=lifespan,
)

app.include_router(src.routers.machines.router)
