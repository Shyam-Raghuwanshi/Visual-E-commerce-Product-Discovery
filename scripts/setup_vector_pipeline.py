#!/usr/bin/env python3
"""
Setup Script for Vector Generation Pipeline

This script sets up the environment and dependencies for vector generation.
"""

import subprocess
import sys
import logging
from pathlib import Path
import json
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        requirements_file = Path(__file__).parent / "requirements_vector.txt"
        
        if not requirements_file.exists():
            logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        logger.info("Installing required packages...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Requirements installed successfully")
            return True
        else:
            logger.error(f"Failed to install requirements: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error installing requirements: {e}")
        return False

def check_qdrant_connection(host="localhost", port=6333):
    """Check if Qdrant is running and accessible"""
    try:
        url = f"http://{host}:{port}/collections"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            logger.info("✓ Qdrant is running and accessible")
            return True
        else:
            logger.warning(f"Qdrant responded with status code: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        logger.warning("✗ Cannot connect to Qdrant")
        logger.info(f"Please ensure Qdrant is running on {host}:{port}")
        return False
    except Exception as e:
        logger.error(f"Error checking Qdrant connection: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    try:
        base_dir = Path(__file__).parent.parent
        directories = [
            base_dir / "data" / "image_cache",
            base_dir / "data" / "vectors",
            base_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created directory: {directory}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False

def check_clip_service():
    """Check if CLIP service is available"""
    try:
        # Add backend to path
        backend_path = Path(__file__).parent.parent / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from app.services.clip_service import CLIPService
        
        # Try to initialize CLIP service
        clip_service = CLIPService(batch_size=1)
        logger.info("✓ CLIP service is available")
        return True
        
    except ImportError as e:
        logger.warning(f"✗ CLIP service not available: {e}")
        logger.info("Please ensure the backend dependencies are installed")
        return False
    except Exception as e:
        logger.warning(f"✗ Error initializing CLIP service: {e}")
        return False

def check_dataset():
    """Check if product dataset exists"""
    dataset_path = Path(__file__).parent.parent / "data" / "product_dataset.json"
    
    if dataset_path.exists():
        try:
            with open(dataset_path, 'r') as f:
                data = json.load(f)
            
            product_count = len(data.get('products', []))
            logger.info(f"✓ Dataset found with {product_count} products")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error reading dataset: {e}")
            return False
    else:
        logger.warning("✗ Product dataset not found")
        logger.info("Please run create_product_dataset.py first")
        return False

def create_config_file():
    """Create default configuration file"""
    try:
        config = {
            "vector_generation": {
                "batch_size": 8,
                "max_concurrent_downloads": 5,
                "text_weight": 0.7,
                "image_weight": 0.3,
                "cache_dir": "data/image_cache",
                "output_dir": "data/vectors"
            },
            "qdrant": {
                "host": "localhost",
                "port": 6333,
                "collection_name": "products"
            },
            "clip": {
                "model_name": "openai/clip-vit-base-patch32",
                "device": "auto"
            }
        }
        
        config_path = Path(__file__).parent.parent / "config" / "pipeline_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✓ Configuration file created: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating config file: {e}")
        return False

def print_setup_summary(checks):
    """Print setup summary"""
    logger.info("=" * 60)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 60)
    
    for check_name, status in checks.items():
        status_symbol = "✓" if status else "✗"
        logger.info(f"{status_symbol} {check_name}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        logger.info("\n🎉 Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Ensure Qdrant is running (if not already)")
        logger.info("2. Run: python vector_generation_pipeline.py")
    else:
        logger.warning("\n⚠️  Setup completed with warnings")
        logger.info("\nPlease address the failed checks before running the pipeline")
    
    logger.info("=" * 60)

def main():
    """Main setup function"""
    logger.info("Starting vector generation pipeline setup...")
    
    checks = {}
    
    # Run all checks
    checks["Python version"] = check_python_version()
    
    if checks["Python version"]:
        checks["Package installation"] = install_requirements()
        checks["Directory setup"] = setup_directories()
        checks["Configuration file"] = create_config_file()
        checks["Dataset availability"] = check_dataset()
        checks["CLIP service"] = check_clip_service()
        checks["Qdrant connection"] = check_qdrant_connection()
    
    # Print summary
    print_setup_summary(checks)
    
    return all(checks.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
