from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy import text

from ki_serverentwicklung.database import engine
from ki_serverentwicklung.orders import router as orders_router


def create_app(*, migrate: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        if migrate and engine.dialect.name == "postgresql":
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS "
                        "version INTEGER NOT NULL DEFAULT 1"
                    )
                )
        yield

    app = FastAPI(title="KI Serverentwicklung API", lifespan=lifespan)
    app.include_router(orders_router)
    return app


app = create_app()


def main() -> None:
    uvicorn.run("ki_serverentwicklung.app:app", host="0.0.0.0", port=8000)
