import os
from fastapi import Header, HTTPException, Depends
from typing import Optional

async def verify_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    app_password = os.environ.get("APP_PASSWORD")
    
    # If no password is set in env, we allow access (be careful, but this matches previous behavior)
    if not app_password:
        return True

    # 1. Check X-API-Key
    if x_api_key == app_password:
        return True
        
    # 2. Check Authorization header (could be "Bearer <password>" or just "<password>")
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token == app_password:
            return True

    raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key or Password")
