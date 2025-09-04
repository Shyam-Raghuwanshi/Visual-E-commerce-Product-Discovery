import React, { useState } from 'react';
import { 
  Heart, 
  Share2, 
  Eye, 
  Star, 
  Info,
  Zap,
  Award
} from 'lucide-react';

const ProductCard = ({ 
  product, 
  similarity_score, 
  viewMode = 'grid',
  isSaved = false,
  onSave,
  onShare,
  explanation = null,
  searchParams = {}
}) => {
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  // Format price
  const formatPrice = (price) => {
    if (typeof price === 'number') {
      return `$${price.toFixed(2)}`;
    }
    return price;
  };

  // Format rating
  const formatRating = (rating) => {
    if (typeof rating === 'number') {
      return rating.toFixed(1);
    }
    return rating || '0.0';
  };

  // Generate explanation based on search params and similarity
  const generateExplanation = () => {
    if (explanation) return explanation;
    
    const reasons = [];
    
    if (similarity_score > 0.8) {
      reasons.push("High visual similarity");
    } else if (similarity_score > 0.6) {
      reasons.push("Good visual match");
    }
    
    if (searchParams.query) {
      if (product.name.toLowerCase().includes(searchParams.query.toLowerCase())) {
        reasons.push("Title matches search");
      }
      if (product.description && product.description.toLowerCase().includes(searchParams.query.toLowerCase())) {
        reasons.push("Description matches");
      }
      if (product.category && product.category.toLowerCase().includes(searchParams.query.toLowerCase())) {
        reasons.push("Category matches");
      }
    }
    
    if (product.rating && product.rating > 4.0) {
      reasons.push("Highly rated");
    }
    
    if (product.brand && searchParams.filters?.brands?.includes(product.brand)) {
      reasons.push("Selected brand");
    }
    
    if (reasons.length === 0) {
      return "Relevant to your search";
    }
    
    return reasons.join(" • ");
  };

  // Handle image load
  const handleImageLoad = () => {
    setImageLoading(false);
  };

  // Handle image error
  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
  };

  // Get availability status
  const getAvailabilityStatus = () => {
    if (product.stock_quantity === 0) {
      return { status: 'Out of Stock', color: 'text-red-600 bg-red-50' };
    } else if (product.stock_quantity && product.stock_quantity < 10) {
      return { status: `Only ${product.stock_quantity} left`, color: 'text-orange-600 bg-orange-50' };
    } else {
      return { status: 'In Stock', color: 'text-green-600 bg-green-50' };
    }
  };

  const availability = getAvailabilityStatus();

  // List view layout
  if (viewMode === 'list') {
    return (
      <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 group">
        <div className="flex p-4 space-x-4">
          {/* Product Image */}
          <div className="relative w-32 h-32 flex-shrink-0">
            <div className="w-full h-full bg-gray-200 rounded-lg overflow-hidden">
              {!imageError ? (
                <>
                  {imageLoading && (
                    <div className="w-full h-full bg-gray-200 animate-pulse flex items-center justify-center">
                      <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                    </div>
                  )}
                  <img
                    src={product.image_url || '/api/placeholder/300/300'}
                    alt={product.name}
                    className={`w-full h-full object-cover transition-all duration-300 group-hover:scale-105 ${
                      imageLoading ? 'opacity-0' : 'opacity-100'
                    }`}
                    onLoad={handleImageLoad}
                    onError={handleImageError}
                  />
                </>
              ) : (
                <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-8 h-8 mx-auto mb-2 bg-gray-300 rounded"></div>
                    <p className="text-xs text-gray-500">No image</p>
                  </div>
                </div>
              )}
            </div>

            {/* Similarity Score Badge */}
            {similarity_score && (
              <div className="absolute top-2 left-2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
                {Math.round(similarity_score * 100)}% match
              </div>
            )}

            {/* Quick Actions Overlay */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
              <button className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors">
                <Eye className="w-4 h-4 text-gray-700" />
              </button>
            </div>
          </div>

          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900 text-lg line-clamp-2 pr-4">
                {product.name}
              </h3>
              
              {/* Action Buttons */}
              <div className="flex space-x-2 flex-shrink-0">
                <button
                  onClick={onSave}
                  className={`p-2 rounded-full transition-all duration-200 ${
                    isSaved 
                      ? 'bg-red-50 text-red-600 hover:bg-red-100' 
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Heart className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
                </button>
                <button
                  onClick={onShare}
                  className="p-2 rounded-full bg-gray-50 text-gray-600 hover:bg-gray-100 transition-colors"
                >
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Price and Rating */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <span className="text-2xl font-bold text-green-600">
                  {formatPrice(product.price)}
                </span>
                {product.original_price && product.original_price > product.price && (
                  <span className="text-sm text-gray-500 line-through">
                    {formatPrice(product.original_price)}
                  </span>
                )}
              </div>
              
              {product.rating && (
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="text-sm font-medium text-gray-700">
                    {formatRating(product.rating)}
                  </span>
                  {product.review_count && (
                    <span className="text-xs text-gray-500">
                      ({product.review_count.toLocaleString()})
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Description */}
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {product.description}
            </p>

            {/* Tags and Availability */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                {product.category && (
                  <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
                    {product.category}
                  </span>
                )}
                {product.brand && (
                  <span className="inline-block bg-blue-50 text-blue-800 text-xs px-2 py-1 rounded">
                    {product.brand}
                  </span>
                )}
              </div>
              
              <span className={`text-xs px-2 py-1 rounded-full ${availability.color}`}>
                {availability.status}
              </span>
            </div>

            {/* Why this matches */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-700 transition-colors"
              >
                <Info className="w-3 h-3" />
                <span>Why this matches</span>
              </button>
              
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                View Details
              </button>
            </div>

            {/* Explanation */}
            {showExplanation && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-800">
                  <Zap className="w-3 h-3 inline mr-1" />
                  {generateExplanation()}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Grid view layout (default)
  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-200 group overflow-hidden">
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden">
        {!imageError ? (
          <>
            {imageLoading && (
              <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
              </div>
            )}
            <img
              src={product.image_url || '/api/placeholder/300/300'}
              alt={product.name}
              className={`w-full h-full object-cover transition-all duration-300 group-hover:scale-110 ${
                imageLoading ? 'opacity-0' : 'opacity-100'
              }`}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          </>
        ) : (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 bg-gray-300 rounded"></div>
              <p className="text-sm text-gray-500">No image available</p>
            </div>
          </div>
        )}

        {/* Badges */}
        <div className="absolute top-3 left-3 space-y-2">
          {similarity_score && (
            <div className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium shadow-lg">
              {Math.round(similarity_score * 100)}% match
            </div>
          )}
          {product.is_featured && (
            <div className="bg-yellow-500 text-white px-2 py-1 rounded text-xs font-medium shadow-lg flex items-center">
              <Award className="w-3 h-3 mr-1" />
              Featured
            </div>
          )}
          {product.is_new && (
            <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-medium shadow-lg">
              New
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="absolute top-3 right-3 space-y-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0">
          <button
            onClick={onSave}
            className={`block p-2 rounded-full shadow-lg transition-all duration-200 ${
              isSaved 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Heart className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
          <button
            onClick={onShare}
            className="block p-2 bg-white text-gray-600 rounded-full shadow-lg hover:bg-gray-50 transition-colors"
          >
            <Share2 className="w-4 h-4" />
          </button>
          <button className="block p-2 bg-white text-gray-600 rounded-full shadow-lg hover:bg-gray-50 transition-colors">
            <Eye className="w-4 h-4" />
          </button>
        </div>

        {/* Availability Overlay */}
        <div className="absolute bottom-3 right-3">
          <span className={`text-xs px-2 py-1 rounded-full shadow-lg backdrop-blur-sm ${availability.color}`}>
            {availability.status}
          </span>
        </div>
      </div>
      
      {/* Product Info */}
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-gray-900 line-clamp-2 pr-2 flex-1">
            {product.name}
          </h3>
        </div>
        
        {/* Rating */}
        {product.rating && (
          <div className="flex items-center space-x-1 mb-2">
            <div className="flex">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-3 h-3 ${
                    star <= Math.floor(product.rating) 
                      ? 'text-yellow-400 fill-current' 
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-gray-600">
              {formatRating(product.rating)}
            </span>
            {product.review_count && (
              <span className="text-xs text-gray-500">
                ({product.review_count.toLocaleString()})
              </span>
            )}
          </div>
        )}

        {/* Description */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {product.description}
        </p>
        
        {/* Price */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold text-green-600">
              {formatPrice(product.price)}
            </span>
            {product.original_price && product.original_price > product.price && (
              <span className="text-sm text-gray-500 line-through">
                {formatPrice(product.original_price)}
              </span>
            )}
          </div>
          {product.brand && (
            <span className="text-xs text-gray-500">
              {product.brand}
            </span>
          )}
        </div>
        
        {/* Category and Tags */}
        <div className="flex items-center justify-between mb-4">
          {product.category && (
            <span className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {product.category}
            </span>
          )}
        </div>

        {/* Why this matches */}
        <button
          onClick={() => setShowExplanation(!showExplanation)}
          className="w-full flex items-center justify-center space-x-1 text-xs text-blue-600 hover:text-blue-700 transition-colors mb-3 py-1"
        >
          <Info className="w-3 h-3" />
          <span>Why this matches</span>
        </button>

        {/* Explanation */}
        {showExplanation && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-800">
              <Zap className="w-3 h-3 inline mr-1" />
              {generateExplanation()}
            </p>
          </div>
        )}
        
        {/* Action Button */}
        <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-all duration-200 font-medium flex items-center justify-center space-x-2 group/btn">
          <Eye className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
          <span>View Details</span>
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
