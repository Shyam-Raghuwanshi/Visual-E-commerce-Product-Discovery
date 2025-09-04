from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.schemas import UploadResponse
from app.services.image_service import ImageService
from datetime import datetime
import aiofiles
import os

router = APIRouter()
image_service = ImageService()

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for product search"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return UploadResponse(
        filename=file.filename,
        file_size=len(content),
        content_type=file.content_type,
        upload_time=datetime.now()
    )

@router.post("/search/image")
async def search_by_image(file: UploadFile = File(...)):
    """Search for products using an uploaded image"""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Process image and search
    results = await image_service.search_by_image(file)
    return results
