"""Main entry point for the FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.endpoints import router as api_router
from app.core.config import settings

# Creating FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A voice bot that responds to personal questions as you would respond to them.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including API router
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint that returns basic information about the API."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "A voice bot that responds to personal questions as you would respond to them.",
        "endpoints": {
            "api": "/api",
            "docs": "/docs" if settings.DEBUG else None,
            "redoc": "/redoc" if settings.DEBUG else None,
        },
    }


# Run the application using uvicorn if this file is run directly
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
