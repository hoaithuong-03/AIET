from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from app.config import settings
from app.routers import health, crawl, ai
 
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions
    print("Starting up...")
    yield
    # Shutdown actions
    print("Shutting down...")
 
 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="""
        This is a sample FastAPI application for Data Processing Services.
        It provides various endpoints to process and analyze data efficiently.
        """,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(crawl.router)
    app.include_router(ai.router)

    # Static files & UI
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": settings.app_version}

    @app.get("/")
    async def read_index():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "AI Story Agent UI not found. Please check src/app/static/index.html"}


    return app
 
 
# Create the FastAPI app instance
app = create_app()
 
 
def run() -> None:
    import uvicorn
 
    port = int(os.getenv("PORT", settings.port))
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        log_level=settings.log_level.lower(),
    )

 
 
if __name__ == "__main__":
    run()
    
    
#poetry run uvicorn app.main:app --reload - chay 
