import logging
import asyncio
from contextlib import suppress
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import store
from app.services.audio import cleanup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app):
    store.initialize()
    cleanup()

    async def expire_media():
        while True:
            await asyncio.sleep(300)
            await asyncio.to_thread(cleanup)

    retention_task = asyncio.create_task(expire_media())
    try:
        yield
    finally:
        retention_task.cancel()
        with suppress(asyncio.CancelledError):
            await retention_task


app = FastAPI(title="iTantra Research Transceiver", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
