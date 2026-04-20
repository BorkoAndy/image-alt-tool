from fastapi import APIRouter, Depends, HTTPException
from .models import AnalysisRequest, AnalysisResponse, HealthResponse
from .auth import verify_auth
from ..lib.vision import analyze_image, analyze_image_multi
import logging

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest, auth: bool = Depends(verify_auth)):
    try:
        if not request.url and not request.image_data:
            raise HTTPException(status_code=400, detail="Image URL or Image Data is required")

        if request.languages:
            meta, limits = analyze_image_multi(
                image_url=request.url,
                base64_data=request.image_data,
                model=request.model,
                languages=request.languages
            )
            return {"meta": meta, "limits": limits}
        else:
            alt_text, limits = analyze_image(
                image_url=request.url,
                base64_data=request.image_data,
                model=request.model,
                lang=request.lang
            )
            return {"alt_text": alt_text, "limits": limits}

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
