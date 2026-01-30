from fastapi import FastAPI
from .routers import tasks_router, auth_router
from .settings import settings

app = FastAPI(title="Task Manager API")

app.include_router(tasks_router.router)
app.include_router(auth_router.router)

@app.get("/")
def home():
    return {
        "message": "Task Manager API is running",
        "version": app.version,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )