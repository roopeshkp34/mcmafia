import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.api.api import router as api_router
from app.services.syncer import syncer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the syncer in the background
    syncer_task = asyncio.create_task(syncer.run())
    yield
    # Clean up if needed
    syncer_task.cancel()
    try:
        await syncer_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
