#!/usr/bin/env python3
"""
Complete Dataset Creation Demonstration

This script demonstrates the complete workflow of creating, validating, 
and preparing product datasets for the Visual E-commerce Product Discovery system.

Usage:
    python demo_dataset_workflow.py

Author: Visual E-commerce Team
Date: September 2025
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_workflow():
    """Demonstrate the complete dataset creation workflow"""
    
    print("\n" + "=" * 80)
    print("🚀 VISUAL E-COMMERCE PRODUCT DISCOVERY - DATASET CREATION DEMO")
    print("=" * 80)
    
    # Step 1: Environment Check
    print(f"\n📋 Step 1: Environment Check")
    print("-" * 40)
    
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python Version: {python_version}")
    
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    scripts_dir = project_root / "scripts"
    
    print(f"✅ Project Root: {project_root}")
    print(f"✅ Data Directory: {data_dir}")
    print(f"✅ Scripts Directory: {scripts_dir}")
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    
    # Step 2: Dependency Check
    print(f"\n🔍 Step 2: Dependency Check")
    print("-" * 40)
    
    # Check basic dependencies
    basic_deps = ["json", "uuid", "random", "logging", "datetime", "pathlib", "re", "collections"]
    for dep in basic_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
    
    # Check enhanced dependencies
    enhanced_deps = ["pandas", "numpy", "datasets", "transformers"]
    enhanced_available = True
    
    for dep in enhanced_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} (enhanced)")
        except ImportError:
            print(f"⚠️  {dep} (enhanced) - optional")
            enhanced_available = False
    
    # Step 3: Basic Dataset Creation
    print(f"\n🏗️  Step 3: Basic Dataset Creation")
    print("-" * 40)
    
    try:
        # Add scripts directory to path
        sys.path.insert(0, str(scripts_dir))
        
        from create_product_dataset import ProductDatasetGenerator
        
        print("Creating basic product dataset...")
        generator = ProductDatasetGenerator()
        
        # Generate smaller dataset for demo
        products = generator.generate_dataset(100)  # Small demo dataset
        
        if products:
            print(f"✅ Generated {len(products)} products")
            
            # Export dataset
            output_file = data_dir / "demo_product_dataset.json"
            generator.export_to_json(products, str(output_file))
            print(f"✅ Exported to: {output_file}")
            
            # Generate statistics
            stats = generator.generate_statistics(products)
            print(f"✅ Dataset Statistics:")
            print(f"   - Categories: {list(stats.get('categories', {}).keys())}")
            print(f"   - Price Range: ${stats.get('price_range', {}).get('min', 0):.2f} - ${stats.get('price_range', {}).get('max', 0):.2f}")
            print(f"   - Available Products: {stats.get('availability', {}).get('available', 0)}")
            
        else:
            print("❌ Failed to generate products")
            return False
    
    except Exception as e:
        print(f"❌ Basic dataset creation failed: {e}")
        return False
    
    # Step 4: Dataset Validation
    print(f"\n🔍 Step 4: Dataset Validation")
    print("-" * 40)
    
    try:
        from validate_dataset import DatasetValidator
        
        validator = DatasetValidator()
        results = validator.validate_dataset(str(output_file))
        
        print(f"✅ Validation completed")
        print(f"   - Total Products: {results['statistics']['overview']['total_products']}")
        print(f"   - Quality Score: {results['overall_quality_score']}%")
        
        # Check for issues
        type_errors = len(results['type_validation']['type_errors'])
        duplicate_ids = len(results['duplicate_detection']['duplicate_ids'])
        
        if type_errors == 0 and duplicate_ids == 0:
            print(f"✅ No critical validation errors found")
        else:
            print(f"⚠️  Found {type_errors} type errors and {duplicate_ids} duplicate IDs")
        
    except Exception as e:
        print(f"❌ Dataset validation failed: {e}")
        return False
    
    # Step 5: Enhanced Dataset (if dependencies available)
    if enhanced_available:
        print(f"\n🚀 Step 5: Enhanced Dataset Creation")
        print("-" * 40)
        
        try:
            from enhanced_dataset_creator import EnhancedDatasetGenerator
            
            enhanced_generator = EnhancedDatasetGenerator()
            enhanced_products = enhanced_generator.create_hybrid_dataset(50)  # Small demo
            
            if enhanced_products:
                # Validate products
                valid_products = []
                for product in enhanced_products:
                    if enhanced_generator.validate_enhanced_product(product):
                        valid_products.append(product)
                
                enhanced_output = data_dir / "demo_enhanced_dataset.json"
                enhanced_generator.export_enhanced_dataset(valid_products, str(enhanced_output))
                
                print(f"✅ Generated {len(valid_products)} enhanced products")
                print(f"✅ Exported to: {enhanced_output}")
                
                # Show source breakdown
                sources = {}
                for product in valid_products:
                    source = product.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                print(f"✅ Source Breakdown: {sources}")
            
        except Exception as e:
            print(f"⚠️  Enhanced dataset creation failed: {e}")
    else:
        print(f"\n⚠️  Step 5: Enhanced Dataset Creation (Skipped)")
        print("-" * 40)
        print("Enhanced dependencies not available. To enable:")
        print("pip install pandas numpy datasets transformers torch")
    
    # Step 6: Integration Instructions
    print(f"\n🔗 Step 6: Integration with Backend")
    print("-" * 40)
    
    print("To integrate with the backend system:")
    print("1. Start the backend server:")
    print("   cd backend && uvicorn main:app --reload")
    print("")
    print("2. Load dataset into vector database:")
    print("   python -m app.services.vector_service --load-dataset ../data/demo_product_dataset.json")
    print("")
    print("3. Test CLIP service:")
    print("   python test_clip_service.py")
    print("")
    print("4. Test search functionality:")
    print("   curl -X POST 'http://localhost:8001/search/text' \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"query\": \"blue t-shirt\", \"limit\": 10}'")
    
    # Step 7: Summary
    print(f"\n📊 Step 7: Demo Summary")
    print("-" * 40)
    
    created_files = []
    if (data_dir / "demo_product_dataset.json").exists():
        created_files.append("demo_product_dataset.json")
    if (data_dir / "demo_enhanced_dataset.json").exists():
        created_files.append("demo_enhanced_dataset.json")
    
    print(f"✅ Demo completed successfully!")
    print(f"✅ Created files: {', '.join(created_files)}")
    print(f"✅ Data directory: {data_dir}")
    print("")
    print("Next steps:")
    print("1. Review the generated datasets")
    print("2. Integrate with the backend system")
    print("3. Test the visual search functionality")
    print("4. Scale up to larger datasets as needed")
    
    return True

def show_sample_data():
    """Show sample data structure"""
    print(f"\n📄 Sample Product Data Structure:")
    print("-" * 40)
    
    sample_product = {
        "id": "PROD_DEMO123",
        "name": "Classic Blue Cotton T-Shirt",
        "description": "Comfortable cotton t-shirt perfect for casual wear. Made from premium cotton with a relaxed fit.",
        "category": "clothing",
        "subcategory": "t-shirts",
        "price": 29.99,
        "brand": "Nike",
        "image_url": "https://source.unsplash.com/400x400/?t-shirt,blue,cotton",
        "tags": ["clothing", "t-shirts", "cotton", "blue", "casual", "comfortable"],
        "color": "blue",
        "size": "M",
        "material": "cotton",
        "gender": "Men",
        "season": "All Season",
        "rating": 4.3,
        "review_count": 127,
        "availability": True,
        "created_at": "2025-09-04T10:30:00"
    }
    
    print(json.dumps(sample_product, indent=2))

def main():
    """Main demonstration function"""
    try:
        # Show sample data structure
        show_sample_data()
        
        # Run the complete workflow demonstration
        success = demonstrate_workflow()
        
        if success:
            print(f"\n🎉 Demo completed successfully!")
            print("You can now proceed with the backend integration.")
        else:
            print(f"\n❌ Demo encountered errors.")
            print("Please check the logs and resolve any issues.")
            return 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Demo failed with unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
