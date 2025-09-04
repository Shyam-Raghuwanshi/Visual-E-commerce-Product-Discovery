import React from 'react';

const ProductCard = ({ product, similarity_score }) => {
  return (
    <div className="product-card bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="aspect-square overflow-hidden rounded-t-lg">
        <img
          src={product.image_url || '/api/placeholder/300/300'}
          alt={product.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
          onError={(e) => {
            e.target.src = '/api/placeholder/300/300';
          }}
        />
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
          {product.description}
        </p>
        
        <div className="flex items-center justify-between mb-3">
          <span className="text-lg font-bold text-green-600">
            ${product.price}
          </span>
          {product.brand && (
            <span className="text-sm text-gray-500">
              {product.brand}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
            {product.category}
          </span>
          
          {similarity_score && (
            <span className="text-xs text-blue-600 font-medium">
              {Math.round(similarity_score * 100)}% match
            </span>
          )}
        </div>
        
        <button className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200">
          View Details
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
