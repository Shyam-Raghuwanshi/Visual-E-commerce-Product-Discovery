#!/bin/bash

# Enhanced FastAPI Startup Script
# This script sets up and runs the Visual E-commerce Product Discovery API
# with all enhanced features including authentication, rate limiting, and monitoring

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
WORKERS="${WORKERS:-1}"
RELOAD="${RELOAD:-true}"
LOG_LEVEL="${LOG_LEVEL:-info}"
ENVIRONMENT="${ENVIRONMENT:-development}"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is available
port_available() {
    ! nc -z localhost "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local service_name="$1"
    local host="$2"
    local port="$3"
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name is not available after $max_attempts attempts"
    return 1
}

# Function to setup Python environment
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Check Python version
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Using Python $PYTHON_VERSION"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        print_status "Activating virtual environment (Windows)..."
        source venv/Scripts/activate
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        pip install fastapi uvicorn python-multipart
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking system dependencies..."
    
    # Check Redis (optional for rate limiting)
    if command_exists redis-server; then
        print_success "Redis is available"
        if ! pgrep redis-server >/dev/null; then
            print_status "Starting Redis server..."
            redis-server --daemonize yes --port 6379 2>/dev/null || print_warning "Could not start Redis server"
        fi
    else
        print_warning "Redis not found. Rate limiting will use in-memory storage."
    fi
    
    # Check Qdrant (required for vector search)
    if wait_for_service "Qdrant" "localhost" "6333"; then
        print_success "Qdrant is running"
    else
        print_warning "Qdrant is not running. Starting with docker..."
        if command_exists docker; then
            docker run -d --name qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest 2>/dev/null || print_warning "Could not start Qdrant with Docker"
            wait_for_service "Qdrant" "localhost" "6333" || print_error "Failed to start Qdrant"
        else
            print_error "Qdrant is required but not running, and Docker is not available"
            print_error "Please install and start Qdrant manually: https://qdrant.tech/documentation/quick_start/"
            exit 1
        fi
    fi
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=${ENVIRONMENT}

# API Keys (Change these in production!)
SECRET_KEY=your-secret-key-change-this-in-production
BASIC_API_KEY=basic_api_key_123
PREMIUM_API_KEY=premium_api_key_456
ENTERPRISE_API_KEY=enterprise_api_key_789

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Qdrant Configuration
QDRANT_URL=http://localhost:6333

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=${LOG_LEVEL}
EOF
        print_success "Created .env file with default configuration"
        print_warning "Please update the API keys in .env file for production use!"
    else
        print_success ".env file already exists"
    fi
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
}

# Function to run database migrations/setup
setup_database() {
    print_status "Setting up database and indexes..."
    
    # Run setup script if it exists
    if [ -f "setup_database.py" ]; then
        python setup_database.py
    else
        print_status "No database setup script found"
    fi
}

# Function to validate API configuration
validate_configuration() {
    print_status "Validating API configuration..."
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        print_error "main.py not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Check if required modules exist
    required_files=("app/routes/search.py" "app/services/search_service.py" "app/models/schemas.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_warning "Required file $file not found"
        fi
    done
    
    # Validate Python syntax
    print_status "Validating Python syntax..."
    python -m py_compile main.py || {
        print_error "Syntax error in main.py"
        exit 1
    }
    
    print_success "Configuration validation completed"
}

# Function to start the API server
start_server() {
    print_status "Starting FastAPI server..."
    
    # Check if port is available
    if ! port_available "$API_PORT"; then
        print_error "Port $API_PORT is already in use"
        print_status "Trying to stop existing process..."
        lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Set uvicorn options based on environment
    UVICORN_OPTS="--host $API_HOST --port $API_PORT --log-level $LOG_LEVEL"
    
    if [ "$ENVIRONMENT" = "development" ] && [ "$RELOAD" = "true" ]; then
        UVICORN_OPTS="$UVICORN_OPTS --reload"
        print_status "Starting in development mode with auto-reload"
    else
        UVICORN_OPTS="$UVICORN_OPTS --workers $WORKERS"
        print_status "Starting in production mode with $WORKERS workers"
    fi
    
    # Display startup information
    echo ""
    echo "=================================================="
    echo "  Visual E-commerce Product Discovery API"
    echo "=================================================="
    echo "  Environment: $ENVIRONMENT"
    echo "  Host: $API_HOST"
    echo "  Port: $API_PORT"
    echo "  Workers: $WORKERS"
    echo "  Log Level: $LOG_LEVEL"
    echo "  Docs: http://$API_HOST:$API_PORT/docs"
    echo "  ReDoc: http://$API_HOST:$API_PORT/redoc"
    echo "=================================================="
    echo ""
    
    # Start the server
    exec uvicorn main:app $UVICORN_OPTS
}

# Function to show help
show_help() {
    echo "Enhanced FastAPI Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --setup-only        Only setup environment, don't start server"
    echo "  --check-deps        Only check dependencies"
    echo "  --validate          Only validate configuration"
    echo "  --no-deps-check     Skip dependency checking"
    echo "  --production        Run in production mode"
    echo ""
    echo "Environment Variables:"
    echo "  API_HOST            API host (default: 0.0.0.0)"
    echo "  API_PORT            API port (default: 8000)"
    echo "  WORKERS             Number of workers (default: 1)"
    echo "  RELOAD              Enable auto-reload (default: true)"
    echo "  LOG_LEVEL           Logging level (default: info)"
    echo "  ENVIRONMENT         Environment (default: development)"
    echo ""
    echo "Examples:"
    echo "  $0                  Start API with default settings"
    echo "  $0 --production     Start in production mode"
    echo "  API_PORT=8080 $0    Start on port 8080"
    echo "  $0 --setup-only     Setup environment without starting server"
}

# Main execution
main() {
    local setup_only=false
    local check_deps_only=false
    local validate_only=false
    local skip_deps_check=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --setup-only)
                setup_only=true
                shift
                ;;
            --check-deps)
                check_deps_only=true
                shift
                ;;
            --validate)
                validate_only=true
                shift
                ;;
            --no-deps-check)
                skip_deps_check=true
                shift
                ;;
            --production)
                ENVIRONMENT="production"
                RELOAD="false"
                WORKERS="${WORKERS:-4}"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Print banner
    echo ""
    echo "=================================================="
    echo "  Visual E-commerce Product Discovery API"
    echo "  Enhanced FastAPI with Authentication & Rate Limiting"
    echo "=================================================="
    echo ""
    
    # Execute based on options
    if [ "$check_deps_only" = true ]; then
        check_dependencies
        exit 0
    fi
    
    if [ "$validate_only" = true ]; then
        validate_configuration
        exit 0
    fi
    
    # Normal startup sequence
    setup_python_environment
    setup_environment
    
    if [ "$skip_deps_check" != true ]; then
        check_dependencies
    fi
    
    validate_configuration
    setup_database
    
    if [ "$setup_only" = true ]; then
        print_success "Setup completed successfully!"
        print_status "To start the server, run: $0"
        exit 0
    fi
    
    # Start the server
    start_server
}

# Error handling
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
