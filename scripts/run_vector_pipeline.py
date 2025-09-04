#!/usr/bin/env python3
"""
Vector Pipeline Runner

This script orchestrates the complete vector generation and storage pipeline:
1. Checks dependencies and setup
2. Ensures Qdrant is running
3. Runs dataset creation if needed
4. Executes vector generation pipeline
5. Validates results

Author: Visual E-commerce Team
Date: September 2025
"""

import subprocess
import sys
import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineRunner:
    """Orchestrates the complete vector generation pipeline"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.backend_dir = self.project_root / "backend"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Pipeline configuration
        self.config = {
            'dataset_file': self.data_dir / 'product_dataset.json',
            'processed_dir': self.data_dir / 'processed',
            'vectors_dir': self.data_dir / 'vectors',
            'images_dir': self.data_dir / 'images',
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'collection_name': 'product_vectors'
        }
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'torch',
            'transformers',
            'qdrant_client',
            'PIL',
            'numpy',
            'aiohttp',
            'tqdm'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.debug(f"✓ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"✗ {package}")
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.info("Install missing packages with:")
            logger.info("pip install -r scripts/requirements_vector.txt")
            return False
        
        logger.info("✓ All dependencies are available")
        return True
    
    def check_backend_availability(self) -> bool:
        """Check if backend CLIP service is available"""
        logger.info("Checking backend availability...")
        
        try:
            sys.path.append(str(self.backend_dir))
            from app.services.clip_service import CLIPService
            
            # Try to initialize CLIP service
            clip_service = CLIPService(batch_size=1)
            logger.info("✓ Backend CLIP service is available")
            return True
            
        except ImportError as e:
            logger.error(f"✗ Cannot import CLIP service: {e}")
            return False
        except Exception as e:
            logger.warning(f"CLIP service initialization warning: {e}")
            return True  # Still proceed as it might work during actual run
    
    def check_qdrant_status(self) -> bool:
        """Check if Qdrant is running and accessible"""
        logger.info("Checking Qdrant status...")
        
        try:
            from qdrant_client import QdrantClient
            
            client = QdrantClient(
                host=self.config['qdrant_host'],
                port=self.config['qdrant_port']
            )
            
            collections = client.get_collections()
            logger.info(f"✓ Qdrant is running with {len(collections.collections)} collections")
            return True
            
        except Exception as e:
            logger.warning(f"✗ Qdrant not accessible: {e}")
            return False
    
    def setup_qdrant(self) -> bool:
        """Setup Qdrant if not running"""
        logger.info("Setting up Qdrant...")
        
        try:
            setup_script = self.scripts_dir / "setup_qdrant.py"
            
            if not setup_script.exists():
                logger.error("Qdrant setup script not found")
                return False
            
            # Run Qdrant setup
            result = subprocess.run([
                sys.executable, str(setup_script)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✓ Qdrant setup completed")
                
                # Wait a bit for Qdrant to be ready
                time.sleep(5)
                
                return self.check_qdrant_status()
            else:
                logger.error(f"Qdrant setup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Qdrant setup timed out")
            return False
        except Exception as e:
            logger.error(f"Error setting up Qdrant: {e}")
            return False
    
    def check_dataset_availability(self) -> bool:
        """Check if product dataset exists"""
        logger.info("Checking dataset availability...")
        
        if self.config['dataset_file'].exists():
            try:
                with open(self.config['dataset_file'], 'r') as f:
                    data = json.load(f)
                
                product_count = len(data.get('products', []))
                logger.info(f"✓ Dataset found with {product_count} products")
                return True
                
            except Exception as e:
                logger.error(f"Dataset file is corrupted: {e}")
                return False
        else:
            logger.warning("✗ Dataset not found")
            return False
    
    def create_dataset(self) -> bool:
        """Create product dataset if it doesn't exist"""
        logger.info("Creating product dataset...")
        
        try:
            dataset_script = self.scripts_dir / "create_product_dataset.py"
            
            if not dataset_script.exists():
                logger.error("Dataset creation script not found")
                return False
            
            # Run dataset creation
            result = subprocess.run([
                sys.executable, str(dataset_script)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✓ Dataset created successfully")
                return self.check_dataset_availability()
            else:
                logger.error(f"Dataset creation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Dataset creation timed out")
            return False
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            return False
    
    def run_vector_generation(self) -> bool:
        """Run the vector generation pipeline"""
        logger.info("Running vector generation pipeline...")
        
        try:
            vector_script = self.scripts_dir / "vector_generation_pipeline.py"
            
            if not vector_script.exists():
                logger.error("Vector generation script not found")
                return False
            
            # Run vector generation
            logger.info("This may take a while depending on dataset size...")
            
            result = subprocess.run([
                sys.executable, str(vector_script)
            ], capture_output=False, text=True, timeout=3600)  # 1 hour timeout
            
            if result.returncode == 0:
                logger.info("✓ Vector generation completed successfully")
                return True
            else:
                logger.error("Vector generation failed")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Vector generation timed out")
            return False
        except KeyboardInterrupt:
            logger.info("Vector generation interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Error running vector generation: {e}")
            return False
    
    def validate_results(self) -> Dict[str, Any]:
        """Validate the pipeline results"""
        logger.info("Validating pipeline results...")
        
        validation_results = {
            'dataset_exists': False,
            'dataset_products': 0,
            'qdrant_connected': False,
            'collection_exists': False,
            'vectors_stored': 0,
            'images_cached': 0
        }
        
        try:
            # Check dataset
            if self.config['dataset_file'].exists():
                validation_results['dataset_exists'] = True
                
                with open(self.config['dataset_file'], 'r') as f:
                    data = json.load(f)
                    validation_results['dataset_products'] = len(data.get('products', []))
            
            # Check Qdrant
            try:
                from qdrant_client import QdrantClient
                
                client = QdrantClient(
                    host=self.config['qdrant_host'],
                    port=self.config['qdrant_port']
                )
                
                validation_results['qdrant_connected'] = True
                
                # Check collection
                try:
                    collection_info = client.get_collection(self.config['collection_name'])
                    validation_results['collection_exists'] = True
                    validation_results['vectors_stored'] = collection_info.points_count
                except:
                    pass
                    
            except:
                pass
            
            # Check cached images
            if self.config['images_dir'].exists():
                image_files = list(self.config['images_dir'].glob('*.jpg'))
                validation_results['images_cached'] = len(image_files)
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
        
        return validation_results
    
    def print_results(self, validation_results: Dict[str, Any]):
        """Print pipeline results summary"""
        logger.info("=" * 60)
        logger.info("VECTOR GENERATION PIPELINE RESULTS")
        logger.info("=" * 60)
        
        # Dataset status
        if validation_results['dataset_exists']:
            logger.info(f"✓ Dataset: {validation_results['dataset_products']} products")
        else:
            logger.warning("✗ Dataset: Not found")
        
        # Qdrant status
        if validation_results['qdrant_connected']:
            logger.info("✓ Qdrant: Connected")
            
            if validation_results['collection_exists']:
                logger.info(f"✓ Collection: {validation_results['vectors_stored']} vectors stored")
            else:
                logger.warning("✗ Collection: Not found")
        else:
            logger.warning("✗ Qdrant: Not connected")
        
        # Images status
        logger.info(f"📁 Images cached: {validation_results['images_cached']}")
        
        # Overall status
        if (validation_results['dataset_exists'] and 
            validation_results['qdrant_connected'] and 
            validation_results['collection_exists'] and 
            validation_results['vectors_stored'] > 0):
            logger.info("🎉 Pipeline completed successfully!")
        else:
            logger.warning("⚠️  Pipeline completed with issues")
        
        logger.info("=" * 60)
    
    async def run_pipeline(self, force_recreate: bool = False):
        """Run the complete pipeline"""
        logger.info("🚀 Starting Vector Generation Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            logger.error("❌ Dependencies check failed")
            return False
        
        # Step 2: Check backend
        if not self.check_backend_availability():
            logger.error("❌ Backend check failed")
            return False
        
        # Step 3: Check/setup Qdrant
        if not self.check_qdrant_status():
            if not self.setup_qdrant():
                logger.error("❌ Qdrant setup failed")
                return False
        
        # Step 4: Check/create dataset
        if force_recreate or not self.check_dataset_availability():
            if not self.create_dataset():
                logger.error("❌ Dataset creation failed")
                return False
        
        # Step 5: Run vector generation
        if not self.run_vector_generation():
            logger.error("❌ Vector generation failed")
            return False
        
        # Step 6: Validate results
        validation_results = self.validate_results()
        self.print_results(validation_results)
        
        return True

def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector Generation Pipeline Runner")
    parser.add_argument("--force-recreate", action="store_true",
                       help="Force recreate dataset even if it exists")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check status, don't run pipeline")
    parser.add_argument("--setup-only", action="store_true",
                       help="Only setup dependencies and Qdrant")
    
    args = parser.parse_args()
    
    runner = PipelineRunner()
    
    try:
        if args.check_only:
            # Just check status
            logger.info("Checking pipeline status...")
            validation_results = runner.validate_results()
            runner.print_results(validation_results)
            
        elif args.setup_only:
            # Just setup
            logger.info("Setting up pipeline components...")
            runner.check_dependencies()
            runner.check_backend_availability()
            runner.setup_qdrant()
            
        else:
            # Run full pipeline
            success = asyncio.run(runner.run_pipeline(args.force_recreate))
            
            if success:
                logger.info("✅ Pipeline completed successfully!")
                sys.exit(0)
            else:
                logger.error("❌ Pipeline failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Pipeline runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
