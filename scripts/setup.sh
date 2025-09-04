#!/bin/bash

# Qdrant Database Setup Script
# Automated setup for Visual E-commerce Product Discovery

set -e  # Exit on any error

echo "🚀 Visual E-commerce Product Discovery - Qdrant Setup"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the setup script
echo "🚀 Running Qdrant setup..."
python3 setup_qdrant.py

echo ""
echo "✅ Qdrant setup completed successfully!"
echo "🎯 Your database is ready for the Visual E-commerce Product Discovery platform"
echo ""
echo "Next steps:"
echo "  1. Start your FastAPI backend: cd ../backend && python main.py"
echo "  2. Start your React frontend: cd ../frontend && npm start"
echo "  3. Begin uploading product data and embeddings"
echo ""
