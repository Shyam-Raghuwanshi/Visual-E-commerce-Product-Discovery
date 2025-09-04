from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import search, upload, health, advanced_search
import uvicorn

app = FastAPI(
    title="Visual E-commerce Product Discovery API",
    description="Multi-modal search API for e-commerce products using images and text with advanced indexing and optimization",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(advanced_search.router, prefix="/api", tags=["advanced-search"])

@app.get("/")
async def root():
    return {"message": "Visual E-commerce Product Discovery API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
