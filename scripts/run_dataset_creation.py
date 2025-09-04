#!/usr/bin/env python3
"""
Dataset Creation Runner

This script provides a simple interface to create product datasets:
1. Basic dataset creation (no external dependencies)
2. Enhanced dataset creation (with Hugging Face integration)

Usage:
    python run_dataset_creation.py --mode basic --count 1000
    python run_dataset_creation.py --mode enhanced --count 1200
    python run_dataset_creation.py --mode both --count 1000

Author: Visual E-commerce Team
Date: September 2025
"""

import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check which dependencies are available"""
    deps = {
        "basic": True,  # Basic Python libraries are assumed to be available
        "enhanced": True,
        "missing_packages": []
    }
    
    # Check pandas
    try:
        import pandas
    except ImportError:
        deps["enhanced"] = False
        deps["missing_packages"].append("pandas")
    
    # Check numpy
    try:
        import numpy
    except ImportError:
        deps["enhanced"] = False
        deps["missing_packages"].append("numpy")
    
    # Check datasets
    try:
        import datasets
    except ImportError:
        deps["enhanced"] = False
        deps["missing_packages"].append("datasets")
    
    if deps["enhanced"]:
        logger.info("Enhanced dependencies available")
    else:
        logger.warning(f"Enhanced dependencies not available: {', '.join(deps['missing_packages'])}")
    
    return deps

def run_basic_dataset_creation(count: int = 1000):
    """Run basic dataset creation"""
    try:
        logger.info("Running basic dataset creation...")
        
        # Import and run basic dataset creator
        from create_product_dataset import ProductDatasetGenerator
        
        generator = ProductDatasetGenerator()
        products = generator.generate_dataset(count)
        
        # Export dataset
        output_dir = Path(__file__).parent.parent / "data"
        output_file = output_dir / "product_dataset.json"
        generator.export_to_json(products, str(output_file))
        
        # Generate statistics
        stats = generator.generate_statistics(products)
        stats_file = output_dir / "dataset_statistics.json"
        
        import json
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Basic dataset creation completed: {len(products)} products")
        return True
        
    except Exception as e:
        logger.error(f"Basic dataset creation failed: {e}")
        return False

def run_enhanced_dataset_creation(count: int = 1200):
    """Run enhanced dataset creation"""
    try:
        logger.info("Running enhanced dataset creation...")
        
        # Import and run enhanced dataset creator
        from enhanced_dataset_creator import EnhancedDatasetGenerator
        
        generator = EnhancedDatasetGenerator()
        products = generator.create_hybrid_dataset(count)
        
        # Validate products
        valid_products = []
        for product in products:
            if generator.validate_enhanced_product(product):
                valid_products.append(product)
        
        # Export dataset
        output_dir = Path(__file__).parent.parent / "data"
        output_file = output_dir / "enhanced_product_dataset.json"
        generator.export_enhanced_dataset(valid_products, str(output_file))
        
        logger.info(f"Enhanced dataset creation completed: {len(valid_products)} products")
        return True
        
    except Exception as e:
        logger.error(f"Enhanced dataset creation failed: {e}")
        return False

def install_dependencies():
    """Guide user to install missing dependencies"""
    logger.info("To install missing dependencies, run:")
    logger.info("pip install pandas numpy datasets Pillow requests transformers torch")
    logger.info("\nOr install from requirements file:")
    logger.info("pip install -r requirements.txt")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create product datasets for Visual E-commerce")
    parser.add_argument('--mode', choices=['basic', 'enhanced', 'both'], default='basic',
                       help='Dataset creation mode')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of products to generate')
    parser.add_argument('--install-deps', action='store_true',
                       help='Show dependency installation instructions')
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_dependencies()
        return
    
    # Check dependencies
    deps = check_dependencies()
    
    if args.mode == 'basic' or (args.mode == 'both'):
        logger.info("=" * 50)
        logger.info("BASIC DATASET CREATION")
        logger.info("=" * 50)
        
        success = run_basic_dataset_creation(args.count)
        if not success:
            logger.error("Basic dataset creation failed")
            sys.exit(1)
    
    if args.mode == 'enhanced' or (args.mode == 'both'):
        logger.info("=" * 50)
        logger.info("ENHANCED DATASET CREATION")
        logger.info("=" * 50)
        
        if not deps["enhanced"]:
            logger.error("Enhanced mode requires additional dependencies")
            logger.error(f"Missing packages: {', '.join(deps['missing_packages'])}")
            install_dependencies()
            sys.exit(1)
        
        success = run_enhanced_dataset_creation(args.count)
        if not success:
            logger.error("Enhanced dataset creation failed")
            sys.exit(1)
    
    logger.info("Dataset creation completed successfully!")

if __name__ == "__main__":
    main()
