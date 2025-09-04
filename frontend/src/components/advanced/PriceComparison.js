import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  TrendingDown, 
  TrendingUp, 
  ArrowRight, 
  ExternalLink,
  Heart,
  AlertCircle,
  CheckCircle,
  Star,
  ShoppingCart,
  Percent,
  Clock,
  BarChart3
} from 'lucide-react';

const PriceComparison = ({ 
  product = null,
  alternatives = [],
  onAddToCart = () => {},
  onSaveProduct = () => {},
  loading = false,
  currency = 'USD'
}) => {
  const [sortBy, setSortBy] = useState('price'); // 'price', 'rating', 'savings'
  const [showOnlyDiscounted, setShowOnlyDiscounted] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  const [savedProducts, setSavedProducts] = useState(new Set());

  // Mock price history data
  useEffect(() => {
    if (product) {
      setPriceHistory([
        { date: '2024-01-01', price: product.price * 1.2 },
        { date: '2024-02-01', price: product.price * 1.15 },
        { date: '2024-03-01', price: product.price * 1.1 },
        { date: '2024-04-01', price: product.price }
      ]);
    }
  }, [product]);

  // Format price with currency
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  // Calculate savings
  const calculateSavings = (originalPrice, currentPrice) => {
    if (!originalPrice || originalPrice <= currentPrice) return null;
    const savings = originalPrice - currentPrice;
    const percentage = Math.round((savings / originalPrice) * 100);
    return { amount: savings, percentage };
  };

  // Get price trend
  const getPriceTrend = () => {
    if (priceHistory.length < 2) return null;
    const current = priceHistory[priceHistory.length - 1].price;
    const previous = priceHistory[priceHistory.length - 2].price;
    return current < previous ? 'down' : current > previous ? 'up' : 'stable';
  };

  // Sort alternatives
  const sortedAlternatives = [...alternatives].sort((a, b) => {
    switch (sortBy) {
      case 'price':
        return a.price - b.price;
      case 'rating':
        return (b.rating || 0) - (a.rating || 0);
      case 'savings':
        const savingsA = calculateSavings(a.originalPrice, a.price)?.percentage || 0;
        const savingsB = calculateSavings(b.originalPrice, b.price)?.percentage || 0;
        return savingsB - savingsA;
      default:
        return 0;
    }
  });

  // Filter alternatives
  const filteredAlternatives = showOnlyDiscounted 
    ? sortedAlternatives.filter(alt => calculateSavings(alt.originalPrice, alt.price))
    : sortedAlternatives;

  // Handle save product
  const handleSaveProduct = (productId) => {
    const newSavedProducts = new Set(savedProducts);
    if (newSavedProducts.has(productId)) {
      newSavedProducts.delete(productId);
    } else {
      newSavedProducts.add(productId);
    }
    setSavedProducts(newSavedProducts);
    onSaveProduct(productId);
  };

  const priceTrend = getPriceTrend();

  if (!product) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <DollarSign className="w-8 h-8 mx-auto mb-2" />
          <p>Select a product to see price comparison</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <DollarSign className="w-5 h-5 text-green-600" />
          <h3 className="text-lg font-semibold text-gray-900">Price Comparison</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-blue-500" />
          <span className="text-sm text-gray-600">Market Analysis</span>
        </div>
      </div>

      {/* Main Product */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-4">
          <div className="w-20 h-20 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
            <img 
              src={product.image_url || '/api/placeholder/80/80'} 
              alt={product.name}
              className="w-full h-full object-cover"
            />
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 mb-1">{product.name}</h4>
            <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-2xl font-bold text-green-600">
                  {formatPrice(product.price)}
                </span>
                {product.originalPrice && product.originalPrice > product.price && (
                  <span className="text-sm text-gray-500 line-through">
                    {formatPrice(product.originalPrice)}
                  </span>
                )}
                {calculateSavings(product.originalPrice, product.price) && (
                  <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                    -{calculateSavings(product.originalPrice, product.price).percentage}%
                  </span>
                )}
              </div>
              
              {priceTrend && (
                <div className={`flex items-center space-x-1 text-sm ${
                  priceTrend === 'down' ? 'text-green-600' : priceTrend === 'up' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {priceTrend === 'down' ? (
                    <TrendingDown className="w-4 h-4" />
                  ) : priceTrend === 'up' ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <Clock className="w-4 h-4" />
                  )}
                  <span>
                    {priceTrend === 'down' ? 'Price dropped' : priceTrend === 'up' ? 'Price increased' : 'Price stable'}
                  </span>
                </div>
              )}
            </div>
            
            {product.rating && (
              <div className="flex items-center space-x-1 mt-2">
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <span className="text-sm text-gray-600">{product.rating}</span>
                {product.reviewCount && (
                  <span className="text-xs text-gray-500">({product.reviewCount} reviews)</span>
                )}
              </div>
            )}
          </div>
          
          <div className="flex flex-col space-y-2">
            <button
              onClick={() => handleSaveProduct(product.id)}
              className={`p-2 rounded-full transition-colors ${
                savedProducts.has(product.id)
                  ? 'bg-red-100 text-red-600 hover:bg-red-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Heart className={`w-4 h-4 ${savedProducts.has(product.id) ? 'fill-current' : ''}`} />
            </button>
            
            <button
              onClick={() => onAddToCart(product)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <ShoppingCart className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Price History Chart */}
      {priceHistory.length > 1 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Price History</h4>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-end space-x-2 h-20">
              {priceHistory.map((point, index) => {
                const maxPrice = Math.max(...priceHistory.map(p => p.price));
                const height = (point.price / maxPrice) * 100;
                const isLowest = point.price === Math.min(...priceHistory.map(p => p.price));
                
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div 
                      className={`w-full rounded-t ${isLowest ? 'bg-green-500' : 'bg-blue-400'} transition-all duration-500`}
                      style={{ height: `${height}%` }}
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(point.date).toLocaleDateString('en-US', { month: 'short' })}
                    </div>
                    <div className="text-xs font-medium text-gray-700">
                      {formatPrice(point.price)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-t border-gray-200 pt-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="price">Price (Low to High)</option>
              <option value="rating">Highest Rated</option>
              <option value="savings">Best Savings</option>
            </select>
          </div>
          
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={showOnlyDiscounted}
              onChange={(e) => setShowOnlyDiscounted(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Discounted only</span>
          </label>
        </div>
        
        <div className="text-sm text-gray-600">
          Found {filteredAlternatives.length} alternatives
        </div>
      </div>

      {/* Alternatives */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse border border-gray-200 rounded-lg p-4">
              <div className="flex space-x-4">
                <div className="w-16 h-16 bg-gray-200 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-6 bg-gray-200 rounded w-1/4"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : filteredAlternatives.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>No alternatives found</p>
          {showOnlyDiscounted && (
            <p className="text-sm mt-1">Try removing the discount filter</p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Similar Products</h4>
          <div className="space-y-3">
            {filteredAlternatives.map((alternative, index) => {
              const savings = calculateSavings(alternative.originalPrice, alternative.price);
              const isPriceBetter = alternative.price < product.price;
              const isRatingBetter = (alternative.rating || 0) > (product.rating || 0);
              
              return (
                <div key={alternative.id || index} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <div className="flex items-start space-x-4">
                    <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                      <img 
                        src={alternative.image_url || '/api/placeholder/64/64'} 
                        alt={alternative.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900 mb-1">{alternative.name}</h5>
                          <p className="text-sm text-gray-600 mb-2">{alternative.brand}</p>
                        </div>
                        
                        <div className="flex space-x-2">
                          {isPriceBetter && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <TrendingDown className="w-3 h-3 mr-1" />
                              Better Price
                            </span>
                          )}
                          {isRatingBetter && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              <Star className="w-3 h-3 mr-1" />
                              Higher Rated
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center space-x-2">
                            <span className={`text-lg font-bold ${isPriceBetter ? 'text-green-600' : 'text-gray-900'}`}>
                              {formatPrice(alternative.price)}
                            </span>
                            {alternative.originalPrice && alternative.originalPrice > alternative.price && (
                              <span className="text-sm text-gray-500 line-through">
                                {formatPrice(alternative.originalPrice)}
                              </span>
                            )}
                            {savings && (
                              <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                                -{savings.percentage}%
                              </span>
                            )}
                          </div>
                          
                          {alternative.rating && (
                            <div className="flex items-center space-x-1">
                              <Star className="w-3 h-3 text-yellow-400 fill-current" />
                              <span className="text-sm text-gray-600">{alternative.rating}</span>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleSaveProduct(alternative.id)}
                            className={`p-2 rounded-full transition-colors ${
                              savedProducts.has(alternative.id)
                                ? 'bg-red-100 text-red-600 hover:bg-red-200'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            <Heart className={`w-4 h-4 ${savedProducts.has(alternative.id) ? 'fill-current' : ''}`} />
                          </button>
                          
                          <button
                            onClick={() => onAddToCart(alternative)}
                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                          >
                            Add to Cart
                          </button>
                          
                          <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                            <ExternalLink className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      
                      {/* Price comparison with main product */}
                      {alternative.price !== product.price && (
                        <div className="mt-2 text-xs">
                          {alternative.price < product.price ? (
                            <span className="text-green-600">
                              <TrendingDown className="w-3 h-3 inline mr-1" />
                              {formatPrice(product.price - alternative.price)} cheaper
                            </span>
                          ) : (
                            <span className="text-red-600">
                              <TrendingUp className="w-3 h-3 inline mr-1" />
                              {formatPrice(alternative.price - product.price)} more expensive
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Best Deal Highlight */}
      {filteredAlternatives.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-green-800 mb-1">Best Deal Found</h4>
              <p className="text-sm text-green-700">
                The lowest price is {formatPrice(Math.min(...filteredAlternatives.map(a => a.price)))} - 
                that's {formatPrice(product.price - Math.min(...filteredAlternatives.map(a => a.price)))} less than the original!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PriceComparison;
