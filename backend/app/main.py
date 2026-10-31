import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as api_router
from app.odoo.client import odoo_client

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger("sunflow.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SunFlow API Gateway...")
    odoo_client.authenticate()
    yield
    logger.info("Shutting down SunFlow API Gateway...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Orchestration Gateway for Project SunFlow (Odoo Solar Operations ERP)",
    lifespan=lifespan
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "project": "SunFlow",
        "description": "Unified Solar Operations & Lifecycle ERP Gateway",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
