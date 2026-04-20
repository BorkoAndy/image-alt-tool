from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Image Alt-Text API",
    description="Professional REST API for AI-powered image analysis and alt-text generation.",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the v1 routes
app.include_router(router, prefix="/api/v1", tags=["v1"])

# Root health check
@app.get("/")
async def root():
    return {"message": "Image Alt-Text API is running", "docs": "/api/v1/docs"}
