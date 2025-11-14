"""Application entry point for the sheet import demo API."""
from __future__ import annotations

from fastapi import FastAPI

from api.imports_controller import router as imports_router
from api.upload_controller import router as upload_router

app = FastAPI(title="Sheet Import Demo API")
app.include_router(upload_router)
app.include_router(imports_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
