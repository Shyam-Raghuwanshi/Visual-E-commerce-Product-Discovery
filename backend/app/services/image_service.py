from fastapi import UploadFile
from PIL import Image
import io
from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.models.schemas import SearchResponse

class ImageService:
    def __init__(self):
        self.clip_service = CLIPService()
        self.vector_service = VectorService()
    
    async def search_by_image(self, file: UploadFile) -> SearchResponse:
        """Search for products using an uploaded image"""
        
        # Read and process image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate image embedding using CLIP
        image_embedding = await self.clip_service.encode_image(image)
        
        # Search in vector database
        results = await self.vector_service.search_similar(
            embedding=image_embedding,
            limit=20
        )
        
        return SearchResponse(
            products=results["products"],
            total=results["total"],
            query_time=results.get("query_time", 0.0),
            similarity_scores=results["scores"]
        )
    
    def validate_image(self, file: UploadFile) -> bool:
        """Validate if uploaded file is a valid image"""
        
        valid_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        return file.content_type in valid_types
    
    async def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for CLIP model"""
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to standard size for CLIP
        image = image.resize((224, 224))
        
        return image
