#!/bin/bash

# Demo Scenarios Startup Script
# This script sets up and runs the complete demo scenarios showcase

set -e

echo "🎬 Visual E-commerce Product Discovery - Demo Scenarios Setup"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "DEMO_SCENARIOS_IMPLEMENTATION.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Install Python dependencies
if [ ! -f "venv/bin/activate" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify backend setup
echo "🧪 Testing backend services..."
python -c "
import sys
sys.path.append('.')
try:
    from app.services.demo_scenarios_service import DemoScenariosService
    print('✅ Backend services available')
except ImportError as e:
    print(f'❌ Backend import error: {e}')
    sys.exit(1)
"

cd ..

# Setup frontend
echo "🔧 Setting up frontend..."
cd frontend

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Verify frontend setup
echo "🧪 Testing frontend setup..."
if [ ! -f "src/components/DemoScenariosShowcase.js" ]; then
    echo "❌ Demo scenarios component not found"
    exit 1
fi

echo "✅ Frontend setup complete"
cd ..

# Create demo launcher
echo "📝 Creating demo launcher..."
cat > run_demo.sh << 'EOF'
#!/bin/bash

# Demo Runner Script
echo "🚀 Starting Visual E-commerce Product Discovery Demo"

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "npm.*start" 2>/dev/null || true
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo "🔌 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 10

# Check if backend is running
if ! curl -s http://localhost:8001/api/health > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend running on http://localhost:8001"

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 15

echo "✅ Frontend running on http://localhost:3000"

# Open browser
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "🎉 Demo is ready!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "🎯 Demo Scenarios Available:"
echo "• Celebrity Outfit Recreation"
echo "• Budget-Conscious Shopping"
echo "• Sustainable Fashion Alternatives"
echo "• Size-Inclusive Search"
echo "• Trend Forecasting"
echo ""
echo "Press Ctrl+C to stop the demo"

# Wait for user to stop
wait
EOF

chmod +x run_demo.sh

# Create quick test script
echo "📝 Creating quick test script..."
cat > quick_test.sh << 'EOF'
#!/bin/bash

echo "🧪 Quick Demo Test"

cd backend
source venv/bin/activate

echo "Testing demo scenarios..."
python -c "
import asyncio
import sys
sys.path.append('.')

async def quick_test():
    try:
        from app.services.demo_scenarios_service import DemoScenariosService
        service = DemoScenariosService()
        
        print('✅ Demo service initialized')
        
        # Quick celebrity test
        result = await service.celebrity_outfit_recreation()
        print(f'✅ Celebrity demo: {result[\"celebrity_inspiration\"][\"name\"]}')
        
        # Quick budget test
        result = await service.budget_conscious_shopping('casual wear', 100)
        print(f'✅ Budget demo: {len(result[\"budget_products\"])} products found')
        
        print('🎉 All demos working!')
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        sys.exit(1)

asyncio.run(quick_test())
"
EOF

chmod +x quick_test.sh

# Create comprehensive demo script
echo "📝 Creating comprehensive demo script..."
cat > run_comprehensive_demo.sh << 'EOF'
#!/bin/bash

echo "🎬 Running Comprehensive Demo Scenarios"

cd backend
source venv/bin/activate

echo "Starting comprehensive demo..."
python ../demo_scenarios_showcase.py

echo "Demo complete! Check the generated results file."
EOF

chmod +x run_comprehensive_demo.sh

echo ""
echo "🎉 Demo Scenarios Setup Complete!"
echo "================================================"
echo ""
echo "📋 Available commands:"
echo "• ./quick_test.sh          - Quick functionality test"
echo "• ./run_demo.sh           - Start full interactive demo"
echo "• ./run_comprehensive_demo.sh - Run all demo scenarios"
echo ""
echo "🚀 To start the demo immediately:"
echo "   ./run_demo.sh"
echo ""
echo "📚 Documentation:"
echo "   DEMO_SCENARIOS_IMPLEMENTATION.md"
echo ""
echo "🔧 Manual startup:"
echo "   Backend:  cd backend && source venv/bin/activate && python main.py"
echo "   Frontend: cd frontend && npm start"
echo ""
echo "Happy demoing! 🎉"
