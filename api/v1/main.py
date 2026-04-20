from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router, analyze
from .models import AnalysisRequest
from .auth import verify_auth
from fastapi import Depends

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

# Legacy endpoint support
@app.post("/api/analyze", tags=["legacy"])
async def legacy_analyze(request: AnalysisRequest, auth: bool = Depends(verify_auth)):
    return await analyze(request, auth)

# Root health check
@app.get("/")
async def root():
    return {"message": "Image Alt-Text API is running", "docs": "/api/v1/docs"}
