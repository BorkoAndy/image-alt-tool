from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    image_data: Optional[str] = None
    model: str = "groq"
    languages: Optional[List[str]] = None
    lang: str = "English"

class MetaItem(BaseModel):
    alt: str
    title: str
    caption: str

class AnalysisResponse(BaseModel):
    # For single language mode
    alt_text: Optional[str] = None
    
    # For multi language mode
    meta: Optional[Dict[str, MetaItem]] = None
    
    limits: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
