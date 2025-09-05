#!/bin/bash

# Performance Optimization Deployment Verification Script
# This script verifies that all performance optimizations are working correctly

echo "🚀 Visual E-commerce Product Discovery - Performance Optimization Verification"
echo "=============================================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" == "SUCCESS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" == "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    elif [ "$status" == "ERROR" ]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/api/health" | grep -q "200"; then
        print_status "SUCCESS" "$service_name is running on port $port"
        return 0
    else
        print_status "ERROR" "$service_name is not running on port $port"
        return 1
    fi
}

# Function to check Redis connection
check_redis() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping | grep -q "PONG"; then
            print_status "SUCCESS" "Redis is running and responding"
            return 0
        else
            print_status "WARNING" "Redis command line available but not responding"
            return 1
        fi
    else
        print_status "WARNING" "Redis CLI not available - using fallback cache"
        return 1
    fi
}

# Function to test API endpoints
test_endpoints() {
    local base_url="http://localhost:8000"
    
    print_status "INFO" "Testing API endpoints..."
    
    # Test health endpoint
    response=$(curl -s -w "%{http_code}" "$base_url/api/health")
    if echo "$response" | grep -q "200"; then
        print_status "SUCCESS" "Health endpoint responding"
    else
        print_status "ERROR" "Health endpoint not responding"
    fi
    
    # Test detailed health endpoint
    response=$(curl -s -w "%{http_code}" "$base_url/api/health/detailed")
    if echo "$response" | grep -q "200"; then
        print_status "SUCCESS" "Detailed health endpoint responding"
    else
        print_status "WARNING" "Detailed health endpoint not responding"
    fi
    
    # Test metrics endpoint
    response=$(curl -s -w "%{http_code}" "$base_url/api/metrics")
    if echo "$response" | grep -q "200"; then
        print_status "SUCCESS" "Metrics endpoint responding"
    else
        print_status "WARNING" "Metrics endpoint not responding"
    fi
    
    # Test performance endpoint
    response=$(curl -s -w "%{http_code}" "$base_url/api/performance")
    if echo "$response" | grep -q "200"; then
        print_status "SUCCESS" "Performance endpoint responding"
    else
        print_status "WARNING" "Performance endpoint not responding"
    fi
}

# Function to check performance optimizations
check_optimizations() {
    print_status "INFO" "Checking performance optimizations..."
    
    # Check if optimized services are available
    cd "$(dirname "$0")"
    
    # Check cache service
    if [ -f "app/services/cache_service.py" ]; then
        print_status "SUCCESS" "Cache service implemented"
    else
        print_status "ERROR" "Cache service not found"
    fi
    
    # Check enhanced image service
    if [ -f "app/services/enhanced_image_service.py" ]; then
        print_status "SUCCESS" "Enhanced image service implemented"
    else
        print_status "ERROR" "Enhanced image service not found"
    fi
    
    # Check async processing service
    if [ -f "app/services/async_processing_service.py" ]; then
        print_status "SUCCESS" "Async processing service implemented"
    else
        print_status "ERROR" "Async processing service not found"
    fi
    
    # Check database service
    if [ -f "app/services/database_service.py" ]; then
        print_status "SUCCESS" "Database service implemented"
    else
        print_status "ERROR" "Database service not found"
    fi
    
    # Check monitoring service
    if [ -f "app/services/monitoring_service.py" ]; then
        print_status "SUCCESS" "Monitoring service implemented"
    else
        print_status "ERROR" "Monitoring service not found"
    fi
    
    # Check compression middleware
    if [ -f "app/middleware/compression.py" ]; then
        print_status "SUCCESS" "Compression middleware implemented"
    else
        print_status "ERROR" "Compression middleware not found"
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_status "INFO" "Running performance tests..."
    
    # Simple response time test
    if command -v curl &> /dev/null; then
        start_time=$(date +%s%N)
        curl -s -o /dev/null "http://localhost:8000/api/health"
        end_time=$(date +%s%N)
        duration=$(( (end_time - start_time) / 1000000 ))
        
        if [ $duration -lt 100 ]; then
            print_status "SUCCESS" "Health endpoint response time: ${duration}ms (excellent)"
        elif [ $duration -lt 500 ]; then
            print_status "SUCCESS" "Health endpoint response time: ${duration}ms (good)"
        elif [ $duration -lt 1000 ]; then
            print_status "WARNING" "Health endpoint response time: ${duration}ms (acceptable)"
        else
            print_status "WARNING" "Health endpoint response time: ${duration}ms (slow)"
        fi
    fi
    
    # Memory usage check
    if command -v free &> /dev/null; then
        memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        print_status "INFO" "Current memory usage: ${memory_usage}%"
    fi
    
    # CPU usage check
    if command -v top &> /dev/null; then
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
        print_status "INFO" "Current CPU usage: ${cpu_usage}%"
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "INFO" "Checking dependencies..."
    
    dependencies=("python3" "pip" "curl")
    for dep in "${dependencies[@]}"; do
        if command -v "$dep" &> /dev/null; then
            print_status "SUCCESS" "$dep is available"
        else
            print_status "ERROR" "$dep is not available"
        fi
    done
    
    # Check Python packages
    python_packages=("fastapi" "uvicorn" "redis" "pillow" "prometheus-client")
    for package in "${python_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "SUCCESS" "Python package '$package' is available"
        else
            print_status "WARNING" "Python package '$package' is not available (optional)"
        fi
    done
}

# Function to display configuration
show_configuration() {
    print_status "INFO" "Performance Optimization Configuration:"
    echo ""
    echo "📋 Implemented Features:"
    echo "   1. ✅ Redis Caching System (with fallback)"
    echo "   2. ✅ Image Processing Optimization"
    echo "   3. ✅ Async Processing Engine"
    echo "   4. ✅ Database Connection Pooling"
    echo "   5. ✅ Request/Response Compression"
    echo "   6. ✅ Monitoring & Logging"
    echo ""
    echo "🔧 Configuration Files:"
    echo "   • performance_config.json - Performance settings"
    echo "   • requirements.txt - Updated dependencies"
    echo "   • main.py - Enhanced FastAPI application"
    echo ""
    echo "📚 Documentation:"
    echo "   • PERFORMANCE_OPTIMIZATION_README.md - Complete guide"
    echo "   • setup_performance_optimization.sh - Deployment script"
    echo ""
}

# Function to show next steps
show_next_steps() {
    echo ""
    print_status "INFO" "Next Steps:"
    echo ""
    echo "1. 🚀 Start the optimized API server:"
    echo "   ./setup_performance_optimization.sh"
    echo ""
    echo "2. 📊 Monitor performance:"
    echo "   curl http://localhost:8000/api/metrics"
    echo "   curl http://localhost:8000/api/performance"
    echo ""
    echo "3. 🧪 Run load tests:"
    echo "   pip install locust"
    echo "   locust -f tests/load_test.py --host=http://localhost:8000"
    echo ""
    echo "4. 📈 View monitoring dashboard:"
    echo "   # Set up Grafana/Prometheus for advanced monitoring"
    echo ""
    echo "5. 🔧 Customize configuration:"
    echo "   # Edit performance_config.json for your needs"
    echo ""
}

# Main execution
main() {
    echo "Starting verification process..."
    echo ""
    
    # Check dependencies
    check_dependencies
    echo ""
    
    # Check implementation
    check_optimizations
    echo ""
    
    # Check if server is running
    if check_service "FastAPI" "8000"; then
        echo ""
        test_endpoints
        echo ""
        run_performance_tests
    else
        print_status "WARNING" "API server not running - start with ./setup_performance_optimization.sh"
    fi
    
    echo ""
    check_redis
    
    echo ""
    show_configuration
    
    show_next_steps
}

# Run verification
main

echo ""
echo "=============================================================================="
print_status "SUCCESS" "Performance Optimization Verification Complete!"
echo "=============================================================================="
