from fastapi import FastAPI

from app.core.config import settings
from app.api.api import router as api_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
