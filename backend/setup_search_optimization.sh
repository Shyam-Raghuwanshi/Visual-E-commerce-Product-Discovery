#!/bin/bash

# Setup script for Visual E-commerce Product Discovery - Search Index Optimization
# This script sets up all the components needed for Step 2.3 implementation

echo "🚀 Setting up Visual E-commerce Product Discovery - Search Index Optimization"
echo "============================================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose found"
        
        # Start Qdrant if not already running
        echo "🐳 Starting Qdrant database..."
        cd docker
        docker-compose up -d qdrant
        cd ..
        
        # Wait for Qdrant to be ready
        echo "⏳ Waiting for Qdrant to be ready..."
        sleep 10
        
        # Test Qdrant connection
        if curl -s http://localhost:6333/collections > /dev/null; then
            echo "✅ Qdrant is running and accessible"
        else
            echo "⚠️ Qdrant may not be ready yet. Please wait a moment and check manually."
        fi
    else
        echo "⚠️ Docker Compose not found. Please install docker-compose to auto-start Qdrant."
        echo "   You can manually start Qdrant with: docker run -p 6333:6333 qdrant/qdrant"
    fi
else
    echo "⚠️ Docker not found. Please install Docker to run Qdrant."
    echo "   Alternative: You can use Qdrant Cloud or install Qdrant locally."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/image_cache
mkdir -p data/vectors
mkdir -p logs

# Set up environment variables
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cat > .env << EOL
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# CLIP Model Configuration
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
CLIP_DEVICE=auto

# Search Configuration
SEARCH_SIMILARITY_THRESHOLD=0.1
SEARCH_MAX_RESULTS=100
ANALYTICS_HISTORY_SIZE=10000

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
EOL
    echo "✅ Environment file created"
else
    echo "✅ Environment file already exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. 🔧 Start the API server:"
echo "   python main.py"
echo ""
echo "2. 🧪 Run the comprehensive demo:"
echo "   python demo_search_optimization.py"
echo ""
echo "3. 🧪 Run the test suite:"
echo "   pytest test_optimized_search.py -v"
echo ""
echo "4. 📖 Check the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. 🔍 Test advanced search features:"
echo "   curl -X POST http://localhost:8000/api/search/advanced/hybrid \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"text_query\": \"laptop\", \"categories\": [\"electronics\"], \"limit\": 10}'"
echo ""
echo "Features implemented in Step 2.3:"
echo "✅ Optimized Qdrant indexes for different search types"
echo "✅ Advanced filters for price ranges, categories, brands"
echo "✅ Hybrid search combining similarity and filters"
echo "✅ Multi-factor ranking based on multiple criteria"
echo "✅ Performance monitoring and query analytics"
echo ""
echo "📚 For detailed documentation, see: SEARCH_OPTIMIZATION_README.md"
echo ""
echo "============================================================================="
