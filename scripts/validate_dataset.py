#!/usr/bin/env python3
"""
Dataset Validation and Analysis Script

This script provides comprehensive validation and analysis of generated datasets:
1. Data quality checks
2. Statistical analysis
3. Duplicate detection
4. Export validation
5. Performance metrics

Author: Visual E-commerce Team
Date: September 2025
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetValidator:
    """Comprehensive dataset validation and analysis"""
    
    def __init__(self):
        self.validation_rules = {
            "required_fields": [
                "id", "name", "description", "category", "subcategory", 
                "price", "brand", "image_url", "tags"
            ],
            "optional_fields": [
                "color", "size", "material", "gender", "season", "rating", 
                "review_count", "availability", "created_at"
            ],
            "enhanced_fields": [
                "sku", "weight", "dimensions", "care_instructions", 
                "sustainability_score", "discount_percentage", "stock_quantity", "source"
            ]
        }
        
        self.validation_errors = []
        self.validation_warnings = []
    
    def load_dataset(self, file_path: str) -> Dict[str, Any]:
        """Load dataset from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            logger.info(f"Loaded dataset from {file_path}")
            
            if "products" in dataset:
                return dataset
            else:
                # Assume direct product list format
                return {"products": dataset, "metadata": {}}
                
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def validate_field_presence(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate required and optional field presence"""
        results = {
            "total_products": len(products),
            "field_coverage": {},
            "missing_required": [],
            "missing_optional": []
        }
        
        # Check field coverage
        all_fields = self.validation_rules["required_fields"] + self.validation_rules["optional_fields"]
        
        for field in all_fields:
            count = sum(1 for product in products if field in product and product[field] is not None)
            coverage = (count / len(products)) * 100 if products else 0
            results["field_coverage"][field] = {
                "count": count,
                "coverage_percentage": round(coverage, 2)
            }
        
        # Check for missing required fields
        for i, product in enumerate(products):
            for field in self.validation_rules["required_fields"]:
                if field not in product or product[field] is None or product[field] == "":
                    results["missing_required"].append({
                        "product_index": i,
                        "product_id": product.get("id", "unknown"),
                        "missing_field": field
                    })
        
        return results
    
    def validate_data_types(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data types and formats"""
        results = {
            "type_errors": [],
            "format_errors": [],
            "range_errors": []
        }
        
        for i, product in enumerate(products):
            product_id = product.get("id", f"index_{i}")
            
            # Price validation
            if "price" in product:
                try:
                    price = float(product["price"])
                    if price <= 0:
                        results["range_errors"].append({
                            "product_id": product_id,
                            "field": "price",
                            "value": price,
                            "error": "Price must be positive"
                        })
                except (ValueError, TypeError):
                    results["type_errors"].append({
                        "product_id": product_id,
                        "field": "price",
                        "value": product["price"],
                        "error": "Price must be numeric"
                    })
            
            # Rating validation
            if "rating" in product:
                try:
                    rating = float(product["rating"])
                    if not (0 <= rating <= 5):
                        results["range_errors"].append({
                            "product_id": product_id,
                            "field": "rating",
                            "value": rating,
                            "error": "Rating must be between 0 and 5"
                        })
                except (ValueError, TypeError):
                    results["type_errors"].append({
                        "product_id": product_id,
                        "field": "rating",
                        "value": product["rating"],
                        "error": "Rating must be numeric"
                    })
            
            # URL validation
            if "image_url" in product:
                url = product["image_url"]
                if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                    results["format_errors"].append({
                        "product_id": product_id,
                        "field": "image_url",
                        "value": url,
                        "error": "Invalid URL format"
                    })
            
            # Tags validation
            if "tags" in product:
                tags = product["tags"]
                if not isinstance(tags, list):
                    results["type_errors"].append({
                        "product_id": product_id,
                        "field": "tags",
                        "value": type(tags).__name__,
                        "error": "Tags must be a list"
                    })
        
        return results
    
    def detect_duplicates(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect duplicate products"""
        results = {
            "duplicate_ids": [],
            "duplicate_names": [],
            "similar_products": []
        }
        
        # Check for duplicate IDs
        id_counts = Counter(product.get("id") for product in products if product.get("id"))
        for product_id, count in id_counts.items():
            if count > 1:
                results["duplicate_ids"].append({
                    "id": product_id,
                    "count": count
                })
        
        # Check for duplicate names
        name_counts = Counter(product.get("name") for product in products if product.get("name"))
        for name, count in name_counts.items():
            if count > 1:
                results["duplicate_names"].append({
                    "name": name,
                    "count": count
                })
        
        # Check for similar products (same category, brand, and price)
        similarity_key = lambda p: (
            p.get("category", ""),
            p.get("brand", ""),
            p.get("subcategory", ""),
            round(float(p.get("price", 0)), 0)  # Round price to nearest dollar
        )
        
        similarity_groups = defaultdict(list)
        for i, product in enumerate(products):
            key = similarity_key(product)
            similarity_groups[key].append(i)
        
        for key, indices in similarity_groups.items():
            if len(indices) > 2:  # More than 2 similar products might indicate duplicates
                results["similar_products"].append({
                    "category": key[0],
                    "brand": key[1],
                    "subcategory": key[2],
                    "price_range": key[3],
                    "product_count": len(indices),
                    "product_indices": indices[:5]  # Show first 5 indices
                })
        
        return results
    
    def analyze_data_quality(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall data quality"""
        results = {
            "completeness": {},
            "consistency": {},
            "uniqueness": {},
            "validity": {}
        }
        
        # Completeness analysis
        total_fields = len(self.validation_rules["required_fields"] + self.validation_rules["optional_fields"])
        completeness_scores = []
        
        for product in products:
            filled_fields = sum(1 for field in self.validation_rules["required_fields"] + self.validation_rules["optional_fields"] 
                              if field in product and product[field] is not None and product[field] != "")
            completeness_scores.append(filled_fields / total_fields)
        
        results["completeness"] = {
            "average_completeness": round(sum(completeness_scores) / len(completeness_scores) * 100, 2) if completeness_scores else 0,
            "min_completeness": round(min(completeness_scores) * 100, 2) if completeness_scores else 0,
            "max_completeness": round(max(completeness_scores) * 100, 2) if completeness_scores else 0
        }
        
        # Consistency analysis (check for consistent formatting)
        category_variations = set(product.get("category", "").lower() for product in products)
        brand_variations = len(set(product.get("brand", "") for product in products))
        
        results["consistency"] = {
            "category_variations": len(category_variations),
            "brand_count": brand_variations,
            "categories": list(category_variations)
        }
        
        # Uniqueness analysis
        unique_ids = len(set(product.get("id") for product in products if product.get("id")))
        unique_names = len(set(product.get("name") for product in products if product.get("name")))
        
        results["uniqueness"] = {
            "unique_ids": unique_ids,
            "unique_names": unique_names,
            "id_uniqueness_rate": round((unique_ids / len(products)) * 100, 2) if products else 0,
            "name_uniqueness_rate": round((unique_names / len(products)) * 100, 2) if products else 0
        }
        
        return results
    
    def generate_statistics(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive dataset statistics"""
        if not products:
            return {}
        
        stats = {
            "overview": {
                "total_products": len(products),
                "generated_at": datetime.now().isoformat()
            },
            "categories": {},
            "pricing": {},
            "brands": {},
            "availability": {},
            "ratings": {}
        }
        
        # Category distribution
        categories = [product.get("category", "unknown") for product in products]
        stats["categories"] = dict(Counter(categories))
        
        # Pricing analysis
        prices = [float(product.get("price", 0)) for product in products if product.get("price")]
        if prices:
            stats["pricing"] = {
                "min": round(min(prices), 2),
                "max": round(max(prices), 2),
                "average": round(sum(prices) / len(prices), 2),
                "median": round(sorted(prices)[len(prices) // 2], 2)
            }
        
        # Brand distribution
        brands = [product.get("brand", "unknown") for product in products]
        brand_counts = Counter(brands)
        stats["brands"] = dict(brand_counts.most_common(10))  # Top 10 brands
        
        # Availability analysis
        available_count = sum(1 for product in products if product.get("availability", True))
        stats["availability"] = {
            "available": available_count,
            "unavailable": len(products) - available_count,
            "availability_rate": round((available_count / len(products)) * 100, 2) if products else 0
        }
        
        # Ratings analysis
        ratings = [float(product.get("rating", 0)) for product in products if product.get("rating")]
        if ratings:
            stats["ratings"] = {
                "average": round(sum(ratings) / len(ratings), 2),
                "min": round(min(ratings), 1),
                "max": round(max(ratings), 1),
                "count": len(ratings)
            }
        
        return stats
    
    def validate_dataset(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive dataset validation"""
        logger.info(f"Starting validation of dataset: {file_path}")
        
        # Load dataset
        dataset = self.load_dataset(file_path)
        products = dataset.get("products", [])
        
        if not products:
            logger.error("No products found in dataset")
            return {"error": "No products found"}
        
        # Perform validations
        validation_results = {
            "file_info": {
                "file_path": file_path,
                "file_size_mb": round(Path(file_path).stat().st_size / (1024 * 1024), 2),
                "validation_date": datetime.now().isoformat()
            },
            "field_validation": self.validate_field_presence(products),
            "type_validation": self.validate_data_types(products),
            "duplicate_detection": self.detect_duplicates(products),
            "quality_analysis": self.analyze_data_quality(products),
            "statistics": self.generate_statistics(products)
        }
        
        # Calculate overall quality score
        quality_metrics = validation_results["quality_analysis"]
        field_coverage = validation_results["field_validation"]["field_coverage"]
        
        # Simple quality score calculation
        avg_coverage = sum(field["coverage_percentage"] for field in field_coverage.values()) / len(field_coverage) if field_coverage else 0
        completeness_score = quality_metrics.get("completeness", {}).get("average_completeness", 0)
        uniqueness_score = quality_metrics.get("uniqueness", {}).get("id_uniqueness_rate", 0)
        
        overall_quality = round((avg_coverage + completeness_score + uniqueness_score) / 3, 2)
        validation_results["overall_quality_score"] = overall_quality
        
        logger.info(f"Validation completed. Overall quality score: {overall_quality}%")
        
        return validation_results
    
    def export_validation_report(self, validation_results: Dict[str, Any], output_path: str):
        """Export validation report to JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Validation report exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting validation report: {e}")
            raise

def main():
    """Main function for dataset validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate product datasets")
    parser.add_argument('--input', required=True, help='Input dataset file path')
    parser.add_argument('--output', help='Output validation report path')
    
    args = parser.parse_args()
    
    try:
        # Initialize validator
        validator = DatasetValidator()
        
        # Validate dataset
        results = validator.validate_dataset(args.input)
        
        # Export report
        if args.output:
            validator.export_validation_report(results, args.output)
        else:
            # Print summary to console
            print(f"\n{'='*50}")
            print("DATASET VALIDATION SUMMARY")
            print(f"{'='*50}")
            
            print(f"File: {results['file_info']['file_path']}")
            print(f"Size: {results['file_info']['file_size_mb']} MB")
            print(f"Products: {results['statistics']['overview']['total_products']}")
            print(f"Overall Quality Score: {results['overall_quality_score']}%")
            
            print(f"\nCategories: {', '.join(results['statistics']['categories'].keys())}")
            if 'pricing' in results['statistics']:
                pricing = results['statistics']['pricing']
                print(f"Price Range: ${pricing['min']} - ${pricing['max']} (avg: ${pricing['average']})")
            
            # Show any critical issues
            type_errors = len(results['type_validation']['type_errors'])
            duplicate_ids = len(results['duplicate_detection']['duplicate_ids'])
            
            if type_errors > 0:
                print(f"\n⚠️  Found {type_errors} type validation errors")
            
            if duplicate_ids > 0:
                print(f"⚠️  Found {duplicate_ids} duplicate IDs")
            
            if type_errors == 0 and duplicate_ids == 0:
                print("\n✅ No critical validation errors found")
        
        logger.info("Dataset validation completed successfully")
        
    except Exception as e:
        logger.error(f"Dataset validation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
