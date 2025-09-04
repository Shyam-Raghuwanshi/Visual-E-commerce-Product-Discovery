# Visual E-commerce Product Discovery Platform

A cutting-edge multi-modal e-commerce search platform that enables users to discover products using images, text, or combined queries powered by AI.

## 🚀 Features

- **Image-to-Product Search**: Upload product images to find similar items
- **Advanced Text Search**: Natural language product discovery
- **Multi-Modal Search**: Combine images and text for precise results
- **AI-Powered Matching**: CLIP model for understanding visual and textual content
- **Real-time Results**: Fast vector similarity search with Qdrant
- **Modern UI**: Responsive React frontend with Tailwind CSS

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **CLIP Model**: OpenAI's vision-language model
- **Qdrant**: Vector database for similarity search
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face model library

### Frontend
- **React 18**: Modern UI library
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Lucide React**: Beautiful icons

### Infrastructure
- **Docker**: Containerized database setup
- **Python Virtual Environment**: Isolated dependencies

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Visual-E-commerce-Product-Discovery
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your configurations
nano .env
```

### 3. Start Qdrant Database
```bash
cd docker
docker-compose up -d qdrant
cd ..
```

### 4. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
```

The backend will be available at `http://localhost:8000`

### 5. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
Visual-E-commerce-Product-Discovery/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities and config
│   ├── requirements.txt     # Python dependencies
│   └── main.py             # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   ├── package.json        # Node dependencies
│   └── tailwind.config.js  # Tailwind configuration
├── docker/
│   └── docker-compose.yml  # Database services
├── data/                   # Sample data (optional)
├── .env.template          # Environment variables template
└── README.md              # This file
```

## 🔧 API Endpoints

### Health Check
- `GET /api/health` - API health status

### Search
- `POST /api/search/text` - Text-based product search
- `POST /api/search/image` - Image-based product search
- `POST /api/search/combined` - Combined text and image search
- `GET /api/search/similar/{product_id}` - Get similar products

### Upload
- `POST /api/upload` - Upload product images

### Products
- `GET /api/products/categories` - Get available categories

## 🎯 Usage Examples

### Text Search
```bash
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "red running shoes",
    "category": "sports",
    "limit": 10
  }'
```

### Image Search
```bash
curl -X POST "http://localhost:8000/api/search/image" \
  -F "file=@product_image.jpg" \
  -F "category=electronics"
```

## 🔄 Development Workflow

### Backend Development
```bash
cd backend
source venv/bin/activate

# Install new dependencies
pip install <package-name>
pip freeze > requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install new dependencies
npm install <package-name>

# Start with hot reload
npm start

# Build for production
npm run build
```

## 🚀 Deployment

### Production Backend
```bash
cd backend
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Production Frontend
```bash
cd frontend
npm run build
# Serve the build folder with your preferred web server
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📊 Performance Optimization

1. **Vector Database**: Ensure Qdrant is properly indexed
2. **Model Caching**: CLIP models are cached after first load
3. **Image Processing**: Images are resized for optimal processing
4. **API Caching**: Consider Redis for frequent queries

## 🔒 Security Considerations

- File upload validation and size limits
- CORS configuration for production
- Environment variable security
- API rate limiting (implement as needed)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **CLIP Model Download**: First run downloads the model (~600MB)
2. **CUDA Out of Memory**: Set `DEVICE=cpu` in .env file
3. **Port Conflicts**: Change ports in docker-compose.yml if needed
4. **Qdrant Connection**: Ensure Docker service is running

### Performance Tips

- Use GPU acceleration if available
- Adjust `DEFAULT_SEARCH_LIMIT` for faster responses
- Consider model quantization for production

## 📞 Support

For questions and support, please open an issue in the repository.

---

Built with ❤️ for the Visual E-commerce Product Discovery Hackathon
