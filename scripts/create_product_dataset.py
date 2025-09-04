#!/usr/bin/env python3
"""
Product Dataset Creation Script for Visual E-commerce Product Discovery

This script creates a comprehensive dataset of fashion/product items with:
- 1000+ diverse product entries
- Multiple categories (clothing, accessories, shoes)
- Realistic product information
- Data validation and cleaning
- Export to JSON format

Author: Visual E-commerce Team
Date: September 2025
"""

import json
import random
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import logging
from pathlib import Path
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Product data model with validation"""
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    price: float
    brand: str
    image_url: str
    tags: List[str]
    color: str
    size: str
    material: str
    gender: str
    season: str
    rating: float
    review_count: int
    availability: bool
    created_at: str

class ProductDatasetGenerator:
    """Generates realistic fashion/product dataset"""
    
    def __init__(self):
        self.setup_data_sources()
        
    def setup_data_sources(self):
        """Setup data sources for generating realistic products"""
        
        # Categories and subcategories
        self.categories = {
            "clothing": {
                "subcategories": ["t-shirts", "shirts", "pants", "jeans", "dresses", "skirts", 
                                "jackets", "coats", "sweaters", "hoodies", "blouses", "suits"],
                "materials": ["cotton", "polyester", "wool", "silk", "denim", "linen", "cashmere", "leather"],
                "colors": ["black", "white", "navy", "gray", "brown", "beige", "red", "blue", "green", "pink"]
            },
            "shoes": {
                "subcategories": ["sneakers", "boots", "sandals", "heels", "flats", "loafers", 
                                "running-shoes", "dress-shoes", "casual-shoes", "athletic-shoes"],
                "materials": ["leather", "canvas", "synthetic", "suede", "rubber", "mesh"],
                "colors": ["black", "white", "brown", "tan", "navy", "gray", "red", "blue"]
            },
            "accessories": {
                "subcategories": ["bags", "belts", "watches", "jewelry", "hats", "scarves", 
                                "sunglasses", "wallets", "backpacks", "handbags"],
                "materials": ["leather", "metal", "fabric", "plastic", "wood", "gold", "silver"],
                "colors": ["black", "brown", "gold", "silver", "navy", "red", "white", "tan"]
            }
        }
        
        # Brands by category
        self.brands = {
            "clothing": ["Nike", "Adidas", "Zara", "H&M", "Uniqlo", "Gap", "Levi's", "Tommy Hilfiger", 
                        "Calvin Klein", "Ralph Lauren", "Forever 21", "Urban Outfitters"],
            "shoes": ["Nike", "Adidas", "Converse", "Vans", "New Balance", "Puma", "Reebok", 
                     "Dr. Martens", "Timberland", "Clarks", "Steve Madden", "Jimmy Choo"],
            "accessories": ["Michael Kors", "Coach", "Kate Spade", "Tory Burch", "Fossil", 
                           "Ray-Ban", "Oakley", "Rolex", "Casio", "Gucci", "Prada", "Louis Vuitton"]
        }
        
        # Size options
        self.sizes = {
            "clothing": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
            "shoes": ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12"],
            "accessories": ["One Size", "Small", "Medium", "Large"]
        }
        
        # Gender options
        self.genders = ["Men", "Women", "Unisex", "Kids"]
        
        # Season options
        self.seasons = ["Spring", "Summer", "Fall", "Winter", "All Season"]
        
        # Product name templates
        self.name_templates = {
            "clothing": [
                "{adjective} {material} {subcategory}",
                "{brand} {subcategory}",
                "{adjective} {subcategory}",
                "{color} {material} {subcategory}",
                "{gender}'s {adjective} {subcategory}"
            ],
            "shoes": [
                "{adjective} {material} {subcategory}",
                "{brand} {subcategory}",
                "{color} {subcategory}",
                "{gender}'s {adjective} {subcategory}",
                "{material} {subcategory}"
            ],
            "accessories": [
                "{adjective} {material} {subcategory}",
                "{brand} {subcategory}",
                "{color} {material} {subcategory}",
                "{adjective} {subcategory}",
                "{gender}'s {material} {subcategory}"
            ]
        }
        
        # Adjectives for product names
        self.adjectives = ["Classic", "Modern", "Vintage", "Elegant", "Casual", "Formal", "Sporty", 
                          "Trendy", "Stylish", "Comfortable", "Premium", "Luxury", "Essential", "Basic"]
        
        # Description templates
        self.description_templates = [
            "Elevate your style with this {adjective} {product_name}. Made from high-quality {material}, "
            "this {subcategory} offers both comfort and durability. Perfect for {season} occasions.",
            
            "Discover the perfect blend of style and comfort with our {adjective} {product_name}. "
            "Crafted from premium {material}, this {subcategory} is designed for the modern {gender_lower}.",
            
            "Step into sophistication with this {adjective} {product_name}. Features premium {material} "
            "construction and timeless design. Ideal for both casual and formal settings.",
            
            "Experience unmatched comfort and style with our {adjective} {product_name}. "
            "Made from carefully selected {material}, perfect for {season} wear.",
            
            "Make a statement with this {adjective} {product_name}. Premium {material} construction "
            "ensures durability while maintaining a stylish appearance. A must-have for any wardrobe."
        ]
        
        # Unsplash image collections (fashion-related)
        self.image_collections = [
            "https://source.unsplash.com/400x400/?fashion,clothing",
            "https://source.unsplash.com/400x400/?shoes,footwear",
            "https://source.unsplash.com/400x400/?accessories,bag",
            "https://source.unsplash.com/400x400/?jewelry,watch",
            "https://source.unsplash.com/400x400/?fashion,style"
        ]
    
    def generate_product_id(self) -> str:
        """Generate unique product ID"""
        return f"PROD_{uuid.uuid4().hex[:8].upper()}"
    
    def generate_product_name(self, category: str, subcategory: str, color: str, 
                             material: str, brand: str, gender: str) -> str:
        """Generate realistic product name"""
        template = random.choice(self.name_templates[category])
        adjective = random.choice(self.adjectives)
        
        name = template.format(
            adjective=adjective,
            material=material,
            subcategory=subcategory.replace("-", " ").title(),
            brand=brand,
            color=color.title(),
            gender=gender
        )
        
        return self.clean_text(name)
    
    def generate_description(self, product_name: str, category: str, subcategory: str, 
                           material: str, season: str, gender: str) -> str:
        """Generate detailed product description"""
        template = random.choice(self.description_templates)
        adjective = random.choice(self.adjectives)
        
        description = template.format(
            adjective=adjective.lower(),
            product_name=product_name.lower(),
            material=material.lower(),
            subcategory=subcategory.replace("-", " "),
            season=season.lower(),
            gender_lower=gender.lower()
        )
        
        return self.clean_text(description)
    
    def generate_tags(self, category: str, subcategory: str, color: str, 
                     material: str, brand: str, gender: str, season: str) -> List[str]:
        """Generate relevant tags for the product"""
        tags = [
            category,
            subcategory.replace("-", " "),
            color,
            material,
            brand.lower(),
            gender.lower(),
            season.lower()
        ]
        
        # Add some additional relevant tags
        if category == "clothing":
            tags.extend(["fashion", "apparel", "wear"])
        elif category == "shoes":
            tags.extend(["footwear", "shoes"])
        elif category == "accessories":
            tags.extend(["accessories", "style"])
        
        # Add random style tags
        style_tags = ["trendy", "casual", "formal", "vintage", "modern", "classic"]
        tags.extend(random.sample(style_tags, 2))
        
        # Remove duplicates and clean
        tags = list(set([self.clean_text(tag.lower()) for tag in tags if tag]))
        
        return tags[:10]  # Limit to 10 tags
    
    def generate_price(self, category: str, brand: str) -> float:
        """Generate realistic price based on category and brand"""
        # Base price ranges by category
        price_ranges = {
            "clothing": (15, 200),
            "shoes": (30, 300),
            "accessories": (10, 500)
        }
        
        # Premium brand multiplier
        premium_brands = ["Ralph Lauren", "Tommy Hilfiger", "Calvin Klein", "Coach", 
                         "Michael Kors", "Gucci", "Prada", "Louis Vuitton", "Rolex"]
        
        base_min, base_max = price_ranges[category]
        
        if brand in premium_brands:
            base_min *= 2
            base_max *= 3
        
        price = round(random.uniform(base_min, base_max), 2)
        return price
    
    def generate_image_url(self, category: str, subcategory: str) -> str:
        """Generate image URL (using placeholder service)"""
        # Use a more specific search term
        search_terms = {
            "clothing": f"{subcategory},fashion,clothing",
            "shoes": f"{subcategory},shoes,footwear",
            "accessories": f"{subcategory},accessories,fashion"
        }
        
        search_term = search_terms.get(category, "fashion")
        # Add random number to get different images
        random_id = random.randint(1, 1000)
        
        return f"https://source.unsplash.com/400x400/?{search_term}&sig={random_id}"
    
    def clean_text(self, text: str) -> str:
        """Clean and validate text input"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters except common punctuation
        text = re.sub(r'[^\w\s\-\'\.,!?]', '', text)
        
        return text
    
    def validate_product(self, product: Product) -> bool:
        """Validate product data"""
        try:
            # Check required fields
            if not all([product.id, product.name, product.category, product.price]):
                return False
            
            # Validate price
            if product.price <= 0:
                return False
            
            # Validate rating
            if not (0 <= product.rating <= 5):
                return False
            
            # Validate review count
            if product.review_count < 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def generate_single_product(self) -> Product:
        """Generate a single product with realistic data"""
        # Select category and subcategory
        category = random.choice(list(self.categories.keys()))
        subcategory = random.choice(self.categories[category]["subcategories"])
        
        # Select attributes
        color = random.choice(self.categories[category]["colors"])
        material = random.choice(self.categories[category]["materials"])
        brand = random.choice(self.brands[category])
        size = random.choice(self.sizes[category])
        gender = random.choice(self.genders)
        season = random.choice(self.seasons)
        
        # Generate product details
        product_id = self.generate_product_id()
        name = self.generate_product_name(category, subcategory, color, material, brand, gender)
        description = self.generate_description(name, category, subcategory, material, season, gender)
        price = self.generate_price(category, brand)
        tags = self.generate_tags(category, subcategory, color, material, brand, gender, season)
        image_url = self.generate_image_url(category, subcategory)
        
        # Generate ratings and reviews
        rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 1000)
        availability = random.choice([True, True, True, False])  # 75% available
        
        product = Product(
            id=product_id,
            name=name,
            description=description,
            category=category,
            subcategory=subcategory,
            price=price,
            brand=brand,
            image_url=image_url,
            tags=tags,
            color=color,
            size=size,
            material=material,
            gender=gender,
            season=season,
            rating=rating,
            review_count=review_count,
            availability=availability,
            created_at=datetime.now().isoformat()
        )
        
        return product
    
    def generate_dataset(self, num_products: int = 1000) -> List[Dict[str, Any]]:
        """Generate complete product dataset"""
        logger.info(f"Generating {num_products} products...")
        
        products = []
        
        for i in range(num_products):
            try:
                product = self.generate_single_product()
                
                if self.validate_product(product):
                    products.append(asdict(product))
                else:
                    logger.warning(f"Invalid product generated at index {i}")
                    continue
                
                # Progress logging
                if (i + 1) % 100 == 0:
                    logger.info(f"Generated {i + 1} products...")
                
            except Exception as e:
                logger.error(f"Error generating product {i}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(products)} valid products")
        return products
    
    def export_to_json(self, products: List[Dict[str, Any]], output_path: str):
        """Export products to JSON file"""
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            dataset = {
                "metadata": {
                    "total_products": len(products),
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "categories": list(self.categories.keys()),
                    "description": "Fashion/Product dataset for Visual E-commerce Product Discovery"
                },
                "products": products
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dataset exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            raise
    
    def generate_statistics(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate dataset statistics"""
        if not products:
            return {}
        
        stats = {
            "total_products": len(products),
            "categories": {},
            "brands": {},
            "price_range": {
                "min": min(p["price"] for p in products),
                "max": max(p["price"] for p in products),
                "average": sum(p["price"] for p in products) / len(products)
            },
            "availability": {
                "available": sum(1 for p in products if p["availability"]),
                "unavailable": sum(1 for p in products if not p["availability"])
            }
        }
        
        # Category distribution
        for product in products:
            category = product["category"]
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # Brand distribution
        for product in products:
            brand = product["brand"]
            stats["brands"][brand] = stats["brands"].get(brand, 0) + 1
        
        return stats

def main():
    """Main function to generate and export dataset"""
    try:
        # Initialize generator
        generator = ProductDatasetGenerator()
        
        # Configuration
        num_products = 1200  # Generate extra to account for validation failures
        output_dir = Path(__file__).parent.parent / "data"
        output_file = output_dir / "product_dataset.json"
        stats_file = output_dir / "dataset_statistics.json"
        
        logger.info("Starting product dataset generation...")
        
        # Generate dataset
        products = generator.generate_dataset(num_products)
        
        if not products:
            logger.error("No valid products generated")
            return
        
        # Generate statistics
        stats = generator.generate_statistics(products)
        logger.info(f"Dataset statistics: {json.dumps(stats, indent=2)}")
        
        # Export dataset
        generator.export_to_json(products, str(output_file))
        
        # Export statistics
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info("Dataset generation completed successfully!")
        logger.info(f"Total products: {len(products)}")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Statistics file: {stats_file}")
        
    except Exception as e:
        logger.error(f"Dataset generation failed: {e}")
        raise

if __name__ == "__main__":
    main()
