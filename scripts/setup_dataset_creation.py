#!/usr/bin/env python3
"""
Dataset Creation Setup and Runner

This script provides a comprehensive setup and execution environment for dataset creation:
1. Dependency checking and installation guidance
2. Environment setup
3. Dataset creation with multiple options
4. Validation and quality checks
5. Integration with the main application

Usage:
    python setup_dataset_creation.py --help
    python setup_dataset_creation.py --check-deps
    python setup_dataset_creation.py --create-basic --count 1000
    python setup_dataset_creation.py --create-enhanced --count 1200
    python setup_dataset_creation.py --validate-existing data/product_dataset.json

Author: Visual E-commerce Team
Date: September 2025
"""

import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetSetupManager:
    """Manages dataset creation setup and execution"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.scripts_dir = self.project_root / "scripts"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        
        self.dependencies = {
            "basic": ["json", "uuid", "random", "logging", "datetime", "pathlib"],
            "enhanced": ["pandas", "numpy", "datasets", "transformers", "torch", "requests"],
            "optional": ["Pillow", "matplotlib", "seaborn"]
        }
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
            return False
        
        logger.info(f"Python version: {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependency availability"""
        results = {
            "basic": {"available": [], "missing": []},
            "enhanced": {"available": [], "missing": []},
            "optional": {"available": [], "missing": []}
        }
        
        # Check basic dependencies (should all be available in standard Python)
        for dep in self.dependencies["basic"]:
            try:
                __import__(dep)
                results["basic"]["available"].append(dep)
            except ImportError:
                results["basic"]["missing"].append(dep)
        
        # Check enhanced dependencies
        for dep in self.dependencies["enhanced"]:
            try:
                __import__(dep)
                results["enhanced"]["available"].append(dep)
            except ImportError:
                results["enhanced"]["missing"].append(dep)
        
        # Check optional dependencies
        for dep in self.dependencies["optional"]:
            try:
                __import__(dep)
                results["optional"]["available"].append(dep)
            except ImportError:
                results["optional"]["missing"].append(dep)
        
        return results
    
    def install_dependencies(self, package_type: str = "enhanced") -> bool:
        """Install dependencies using pip"""
        try:
            if package_type == "enhanced":
                packages = ["pandas", "numpy", "datasets", "transformers", "torch", "requests", "Pillow"]
            elif package_type == "basic":
                packages = ["requests"]  # Only external dependency for basic mode
            else:
                logger.error(f"Unknown package type: {package_type}")
                return False
            
            logger.info(f"Installing {package_type} dependencies...")
            
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                      capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    return False
                else:
                    logger.info(f"Successfully installed {package}")
            
            logger.info("All dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return False
    
    def create_basic_dataset(self, count: int = 1000) -> bool:
        """Create basic dataset"""
        try:
            logger.info("=" * 60)
            logger.info("CREATING BASIC DATASET")
            logger.info("=" * 60)
            
            # Import the basic dataset creator
            sys.path.insert(0, str(self.scripts_dir))
            from create_product_dataset import ProductDatasetGenerator
            
            # Create dataset
            generator = ProductDatasetGenerator()
            products = generator.generate_dataset(count)
            
            if not products:
                logger.error("No products generated")
                return False
            
            # Export dataset
            output_file = self.data_dir / "product_dataset.json"
            generator.export_to_json(products, str(output_file))
            
            # Generate statistics
            stats = generator.generate_statistics(products)
            stats_file = self.data_dir / "dataset_statistics.json"
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Basic dataset created successfully!")
            logger.info(f"   Products: {len(products)}")
            logger.info(f"   Output: {output_file}")
            logger.info(f"   Stats: {stats_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create basic dataset: {e}")
            return False
    
    def create_enhanced_dataset(self, count: int = 1200) -> bool:
        """Create enhanced dataset with real data integration"""
        try:
            logger.info("=" * 60)
            logger.info("CREATING ENHANCED DATASET")
            logger.info("=" * 60)
            
            # Check enhanced dependencies
            deps = self.check_dependencies()
            if deps["enhanced"]["missing"]:
                logger.error(f"Missing enhanced dependencies: {', '.join(deps['enhanced']['missing'])}")
                logger.info("Run with --install-deps enhanced to install them")
                return False
            
            # Import the enhanced dataset creator
            sys.path.insert(0, str(self.scripts_dir))
            from enhanced_dataset_creator import EnhancedDatasetGenerator
            
            # Create dataset
            generator = EnhancedDatasetGenerator()
            products = generator.create_hybrid_dataset(count)
            
            # Validate products
            valid_products = []
            for product in products:
                if generator.validate_enhanced_product(product):
                    valid_products.append(product)
            
            if not valid_products:
                logger.error("No valid products generated")
                return False
            
            # Export dataset
            output_file = self.data_dir / "enhanced_product_dataset.json"
            generator.export_enhanced_dataset(valid_products, str(output_file))
            
            logger.info(f"✅ Enhanced dataset created successfully!")
            logger.info(f"   Products: {len(valid_products)}")
            logger.info(f"   Real data: {sum(1 for p in valid_products if p.get('source') != 'synthetic')}")
            logger.info(f"   Synthetic: {sum(1 for p in valid_products if p.get('source') == 'synthetic')}")
            logger.info(f"   Output: {output_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced dataset: {e}")
            return False
    
    def validate_dataset(self, file_path: str) -> bool:
        """Validate existing dataset"""
        try:
            logger.info("=" * 60)
            logger.info("VALIDATING DATASET")
            logger.info("=" * 60)
            
            if not Path(file_path).exists():
                logger.error(f"Dataset file not found: {file_path}")
                return False
            
            # Import validator
            sys.path.insert(0, str(self.scripts_dir))
            from validate_dataset import DatasetValidator
            
            # Validate dataset
            validator = DatasetValidator()
            results = validator.validate_dataset(file_path)
            
            # Export validation report
            report_file = self.data_dir / f"validation_report_{Path(file_path).stem}.json"
            validator.export_validation_report(results, str(report_file))
            
            # Print summary
            logger.info(f"✅ Dataset validation completed!")
            logger.info(f"   File: {file_path}")
            logger.info(f"   Products: {results['statistics']['overview']['total_products']}")
            logger.info(f"   Quality Score: {results['overall_quality_score']}%")
            logger.info(f"   Report: {report_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate dataset: {e}")
            return False
    
    def list_datasets(self):
        """List available datasets"""
        logger.info("=" * 60)
        logger.info("AVAILABLE DATASETS")
        logger.info("=" * 60)
        
        dataset_files = list(self.data_dir.glob("*.json"))
        
        if not dataset_files:
            logger.info("No datasets found in data directory")
            return
        
        for file in dataset_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "products" in data:
                    count = len(data["products"])
                    metadata = data.get("metadata", {})
                    created = metadata.get("generated_at", "unknown")
                else:
                    count = len(data) if isinstance(data, list) else "unknown"
                    created = "unknown"
                
                size_mb = round(file.stat().st_size / (1024 * 1024), 2)
                
                logger.info(f"📊 {file.name}")
                logger.info(f"   Products: {count}")
                logger.info(f"   Size: {size_mb} MB")
                logger.info(f"   Created: {created}")
                logger.info("")
                
            except Exception as e:
                logger.warning(f"Could not read {file.name}: {e}")
    
    def show_setup_guide(self):
        """Show comprehensive setup guide"""
        print("\n" + "=" * 70)
        print("🚀 DATASET CREATION SETUP GUIDE")
        print("=" * 70)
        
        print("\n1. BASIC SETUP (Recommended for getting started)")
        print("   - Uses only standard Python libraries")
        print("   - Creates 1000+ synthetic products")
        print("   - No external API dependencies")
        print("   Command: python setup_dataset_creation.py --create-basic")
        
        print("\n2. ENHANCED SETUP (Advanced features)")
        print("   - Integrates real data from Hugging Face")
        print("   - Creates hybrid datasets (real + synthetic)")
        print("   - Advanced product attributes")
        print("   Command: python setup_dataset_creation.py --install-deps enhanced")
        print("            python setup_dataset_creation.py --create-enhanced")
        
        print("\n3. VALIDATION")
        print("   - Comprehensive data quality checks")
        print("   - Statistical analysis")
        print("   - Export validation reports")
        print("   Command: python setup_dataset_creation.py --validate path/to/dataset.json")
        
        print("\n4. INTEGRATION WITH BACKEND")
        print("   - Load datasets into vector database")
        print("   - Process images with CLIP")
        print("   - Enable visual search")
        print("   See: backend/README.md")
        
        print("\n" + "=" * 70)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Dataset Creation Setup and Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_dataset_creation.py --check-deps
  python setup_dataset_creation.py --create-basic --count 1000
  python setup_dataset_creation.py --install-deps enhanced
  python setup_dataset_creation.py --create-enhanced --count 1200
  python setup_dataset_creation.py --validate data/product_dataset.json
  python setup_dataset_creation.py --list-datasets
        """
    )
    
    parser.add_argument('--check-deps', action='store_true',
                       help='Check dependency availability')
    parser.add_argument('--install-deps', choices=['basic', 'enhanced'],
                       help='Install dependencies for specified mode')
    parser.add_argument('--create-basic', action='store_true',
                       help='Create basic synthetic dataset')
    parser.add_argument('--create-enhanced', action='store_true',
                       help='Create enhanced dataset with real data integration')
    parser.add_argument('--validate', metavar='FILE',
                       help='Validate existing dataset file')
    parser.add_argument('--list-datasets', action='store_true',
                       help='List available datasets')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of products to generate (default: 1000)')
    parser.add_argument('--guide', action='store_true',
                       help='Show setup guide')
    
    args = parser.parse_args()
    
    # Initialize setup manager
    setup_manager = DatasetSetupManager()
    
    # Check Python version
    if not setup_manager.check_python_version():
        return 1
    
    # Show guide if no arguments or --guide specified
    if len(sys.argv) == 1 or args.guide:
        setup_manager.show_setup_guide()
        return 0
    
    success = True
    
    try:
        if args.check_deps:
            deps = setup_manager.check_dependencies()
            
            print("\n" + "=" * 50)
            print("DEPENDENCY CHECK RESULTS")
            print("=" * 50)
            
            for dep_type, results in deps.items():
                print(f"\n{dep_type.upper()} Dependencies:")
                if results["available"]:
                    print(f"  ✅ Available: {', '.join(results['available'])}")
                if results["missing"]:
                    print(f"  ❌ Missing: {', '.join(results['missing'])}")
        
        if args.install_deps:
            success = setup_manager.install_dependencies(args.install_deps)
        
        if args.create_basic:
            success = setup_manager.create_basic_dataset(args.count)
        
        if args.create_enhanced:
            success = setup_manager.create_enhanced_dataset(args.count)
        
        if args.validate:
            success = setup_manager.validate_dataset(args.validate)
        
        if args.list_datasets:
            setup_manager.list_datasets()
    
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    if not success:
        logger.error("Operation failed")
        return 1
    
    logger.info("✅ Operation completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
