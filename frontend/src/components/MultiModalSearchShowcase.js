import React, { useState, useEffect } from 'react';
import { Search, Palette, DollarSign, Shirt, Calendar, Sparkles, TrendingUp, Heart } from 'lucide-react';

const MultiModalSearchShowcase = () => {
  const [activeFeature, setActiveFeature] = useState('color-variations');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Mock product data for demonstration
  const mockProduct = {
    id: "PROD_E17DF3C5",
    name: "Classic Leather Scarves",
    price: 506.12,
    category: "accessories",
    image_url: "https://source.unsplash.com/400x400/?scarves,accessories,fashion&sig=481",
    color: "navy",
    season: "Fall"
  };

  const features = [
    {
      id: 'color-variations',
      title: 'Find Color Variations',
      description: 'Find items that match this outfit but in a different color',
      icon: Palette,
      color: 'bg-purple-500',
      demo: () => findColorVariations()
    },
    {
      id: 'cheaper-alternatives',
      title: 'Cheaper Alternatives',
      description: 'Show me budget-friendly alternatives to luxury items',
      icon: DollarSign,
      color: 'bg-green-500',
      demo: () => findCheaperAlternatives()
    },
    {
      id: 'accessory-matching',
      title: 'Accessory Matching',
      description: 'Find accessories that go with this dress',
      icon: Shirt,
      color: 'bg-blue-500',
      demo: () => findMatchingAccessories()
    },
    {
      id: 'seasonal-recommendations',
      title: 'Seasonal Trends',
      description: 'Seasonal recommendations based on current trends',
      icon: Calendar,
      color: 'bg-orange-500',
      demo: () => getSeasonalRecommendations()
    },
    {
      id: 'style-evolution',
      title: 'Style Evolution',
      description: 'Make this more casual/formal',
      icon: Sparkles,
      color: 'bg-pink-500',
      demo: () => styleEvolution()
    },
    {
      id: 'trending-now',
      title: 'Trending Now',
      description: 'Discover what\'s trending right now',
      icon: TrendingUp,
      color: 'bg-red-500',
      demo: () => getTrendingItems()
    }
  ];

  const findColorVariations = async () => {
    setLoading(true);
    
    // Mock API call - replace with actual API endpoint
    const mockResults = [
      {
        id: "PROD_001",
        name: "Classic Leather Scarves - Red",
        price: 498.00,
        color: "red",
        image_url: "https://source.unsplash.com/400x400/?red,scarves,accessories&sig=1",
        color_match_reason: ["red", "crimson"],
        similarity_score: 0.92
      },
      {
        id: "PROD_002", 
        name: "Classic Leather Scarves - Forest Green",
        price: 512.00,
        color: "green",
        image_url: "https://source.unsplash.com/400x400/?green,scarves,accessories&sig=2",
        color_match_reason: ["green", "forest"],
        similarity_score: 0.89
      },
      {
        id: "PROD_003",
        name: "Classic Leather Scarves - Charcoal",
        price: 501.50,
        color: "black", 
        image_url: "https://source.unsplash.com/400x400/?black,scarves,accessories&sig=3",
        color_match_reason: ["black", "charcoal"],
        similarity_score: 0.94
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const findCheaperAlternatives = async () => {
    setLoading(true);
    
    const mockResults = [
      {
        id: "PROD_ALT_001",
        name: "Affordable Leather-Look Scarves",
        price: 156.32,
        savings: 349.80,
        savings_percentage: 69.1,
        image_url: "https://source.unsplash.com/400x400/?scarves,affordable&sig=4",
        style_similarity: 0.85
      },
      {
        id: "PROD_ALT_002",
        name: "Budget Classic Scarves",
        price: 89.99,
        savings: 416.13,
        savings_percentage: 82.2,
        image_url: "https://source.unsplash.com/400x400/?scarves,budget&sig=5",
        style_similarity: 0.78
      },
      {
        id: "PROD_ALT_003",
        name: "Value Leather Scarves",
        price: 245.00,
        savings: 261.12,
        savings_percentage: 51.6,
        image_url: "https://source.unsplash.com/400x400/?scarves,value&sig=6",
        style_similarity: 0.91
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const findMatchingAccessories = async () => {
    setLoading(true);
    
    const mockResults = [
      {
        category: "bags",
        items: [
          {
            id: "BAG_001",
            name: "Navy Leather Handbag",
            price: 285.00,
            image_url: "https://source.unsplash.com/400x400/?navy,handbag&sig=7",
            compatibility_score: 0.93,
            match_reasons: ["Matching navy color", "Perfect for Fall season"]
          },
          {
            id: "BAG_002", 
            name: "Classic Tote Bag",
            price: 198.50,
            image_url: "https://source.unsplash.com/400x400/?tote,bag&sig=8",
            compatibility_score: 0.87,
            match_reasons: ["Gender-appropriate styling", "Complementary style"]
          }
        ]
      },
      {
        category: "shoes",
        items: [
          {
            id: "SHOE_001",
            name: "Navy Leather Boots",
            price: 350.00,
            image_url: "https://source.unsplash.com/400x400/?navy,boots&sig=9",
            compatibility_score: 0.95,
            match_reasons: ["Matching navy color", "Perfect for Fall season"]
          }
        ]
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const getSeasonalRecommendations = async () => {
    setLoading(true);
    
    const mockResults = [
      {
        id: "SEASONAL_001",
        name: "Cozy Fall Sweater",
        price: 89.99,
        category: "clothing",
        trend_score: 0.94,
        image_url: "https://source.unsplash.com/400x400/?fall,sweater&sig=10",
        seasonal_reasons: ["Features fall-appropriate qualities: warm, cozy", "Designed specifically for fall"]
      },
      {
        id: "SEASONAL_002",
        name: "Autumn Leather Jacket", 
        price: 299.99,
        category: "clothing",
        trend_score: 0.91,
        image_url: "https://source.unsplash.com/400x400/?autumn,leather,jacket&sig=11",
        seasonal_reasons: ["Perfect layering piece", "Earth tones ideal for season"]
      },
      {
        id: "SEASONAL_003",
        name: "Fall Fashion Boots",
        price: 199.99,
        category: "shoes", 
        trend_score: 0.88,
        image_url: "https://source.unsplash.com/400x400/?fall,boots&sig=12",
        seasonal_reasons: ["Weather-appropriate footwear", "Trending fall styles"]
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const styleEvolution = async () => {
    setLoading(true);
    
    const mockResults = [
      {
        id: "STYLE_001",
        name: "Casual Cotton Scarves",
        price: 45.99,
        style_score: 0.89,
        transformation: "casual",
        image_url: "https://source.unsplash.com/400x400/?casual,scarves&sig=13",
        style_reasons: ["Embodies casual, relaxed style elements"]
      },
      {
        id: "STYLE_002",
        name: "Relaxed Knit Scarf",
        price: 32.50,
        style_score: 0.92,
        transformation: "casual", 
        image_url: "https://source.unsplash.com/400x400/?relaxed,knit,scarf&sig=14",
        style_reasons: ["Perfect for laid-back, comfortable styling"]
      },
      {
        id: "STYLE_003",
        name: "Everyday Lightweight Scarf",
        price: 29.99,
        style_score: 0.85,
        transformation: "casual",
        image_url: "https://source.unsplash.com/400x400/?everyday,lightweight,scarf&sig=15", 
        style_reasons: ["Ideal for casual, everyday wear"]
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const getTrendingItems = async () => {
    setLoading(true);
    
    const mockResults = [
      {
        id: "TREND_001",
        name: "Viral TikTok Jacket",
        price: 128.00,
        category: "clothing",
        trend_score: 0.97,
        image_url: "https://source.unsplash.com/400x400/?viral,jacket,trending&sig=16",
        trending_reason: "Featured by 500+ influencers this week"
      },
      {
        id: "TREND_002",
        name: "Instagram Famous Boots", 
        price: 245.00,
        category: "shoes",
        trend_score: 0.94,
        image_url: "https://source.unsplash.com/400x400/?instagram,famous,boots&sig=17",
        trending_reason: "Spotted on 12 celebrities this month"
      },
      {
        id: "TREND_003",
        name: "Pinterest Popular Bag",
        price: 89.99,
        category: "accessories",
        trend_score: 0.91,
        image_url: "https://source.unsplash.com/400x400/?pinterest,popular,bag&sig=18",
        trending_reason: "Saved 50K+ times in the last week"
      }
    ];

    setTimeout(() => {
      setSearchResults(mockResults);
      setLoading(false);
    }, 1500);
  };

  const renderResults = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <span className="ml-3 text-gray-600">Searching with AI-powered vector similarity...</span>
        </div>
      );
    }

    if (searchResults.length === 0) {
      return (
        <div className="text-center py-12">
          <Search className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No search performed</h3>
          <p className="mt-1 text-sm text-gray-500">
            Select a feature above to see AI-powered search results
          </p>
        </div>
      );
    }

    // Handle accessory matching results (nested structure)
    if (activeFeature === 'accessory-matching' && searchResults[0]?.category) {
      return (
        <div className="space-y-6">
          {searchResults.map((categoryGroup, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 capitalize">
                {categoryGroup.category}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {categoryGroup.items.map((item) => (
                  <div key={item.id} className="border rounded-lg p-3 hover:shadow-md transition-shadow">
                    <img 
                      src={item.image_url} 
                      alt={item.name}
                      className="w-full h-32 object-cover rounded-md mb-2"
                    />
                    <h4 className="font-medium text-sm text-gray-900">{item.name}</h4>
                    <p className="text-lg font-bold text-indigo-600">${item.price}</p>
                    <div className="mt-2">
                      <div className="flex items-center">
                        <span className="text-xs text-gray-500">Compatibility:</span>
                        <div className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                          {Math.round(item.compatibility_score * 100)}%
                        </div>
                      </div>
                      {item.match_reasons && (
                        <div className="mt-1">
                          {item.match_reasons.map((reason, reasonIdx) => (
                            <span key={reasonIdx} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                              {reason}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      );
    }

    // Handle regular results
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {searchResults.map((product) => (
          <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
            <img 
              src={product.image_url} 
              alt={product.name}
              className="w-full h-48 object-cover"
            />
            <div className="p-4">
              <h3 className="font-semibold text-gray-900">{product.name}</h3>
              <p className="text-2xl font-bold text-indigo-600 mt-1">${product.price}</p>
              
              {/* Feature-specific details */}
              {activeFeature === 'color-variations' && product.color_match_reason && (
                <div className="mt-2">
                  <span className="text-sm text-gray-600">Color matches:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {product.color_match_reason.map((color, idx) => (
                      <span key={idx} className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {activeFeature === 'cheaper-alternatives' && product.savings && (
                <div className="mt-2">
                  <div className="bg-green-100 text-green-800 text-sm px-2 py-1 rounded">
                    Save ${product.savings.toFixed(2)} ({product.savings_percentage.toFixed(1)}%)
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Style similarity: {Math.round(product.style_similarity * 100)}%
                  </div>
                </div>
              )}
              
              {activeFeature === 'seasonal-recommendations' && product.seasonal_reasons && (
                <div className="mt-2">
                  <div className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded mb-2">
                    Trend Score: {Math.round(product.trend_score * 100)}%
                  </div>
                  {product.seasonal_reasons.map((reason, idx) => (
                    <p key={idx} className="text-xs text-gray-600">{reason}</p>
                  ))}
                </div>
              )}
              
              {activeFeature === 'style-evolution' && product.style_reasons && (
                <div className="mt-2">
                  <div className="bg-pink-100 text-pink-800 text-xs px-2 py-1 rounded mb-2">
                    Style Match: {Math.round(product.style_score * 100)}%
                  </div>
                  {product.style_reasons.map((reason, idx) => (
                    <p key={idx} className="text-xs text-gray-600">{reason}</p>
                  ))}
                </div>
              )}
              
              {activeFeature === 'trending-now' && product.trending_reason && (
                <div className="mt-2">
                  <div className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded mb-2">
                    Trending: {Math.round(product.trend_score * 100)}%
                  </div>
                  <p className="text-xs text-gray-600">{product.trending_reason}</p>
                </div>
              )}
              
              <button className="w-full mt-4 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🚀 Multi-Modal Search Enhancement
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Showcase advanced vector search capabilities with AI-powered product discovery
        </p>
      </div>

      {/* Reference Product Card */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-6 mb-8 text-white">
        <div className="flex items-center space-x-4">
          <img 
            src={mockProduct.image_url} 
            alt={mockProduct.name}
            className="w-24 h-24 object-cover rounded-lg"
          />
          <div>
            <h2 className="text-2xl font-bold">{mockProduct.name}</h2>
            <p className="text-indigo-100">Reference Product for AI Search</p>
            <div className="flex items-center space-x-4 mt-2">
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                ${mockProduct.price}
              </span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                {mockProduct.category}
              </span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                {mockProduct.color}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {features.map((feature) => {
          const IconComponent = feature.icon;
          return (
            <button
              key={feature.id}
              onClick={() => {
                setActiveFeature(feature.id);
                setSearchResults([]);
                feature.demo();
              }}
              className={`p-4 rounded-lg border-2 transition-all ${
                activeFeature === feature.id
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center mb-3`}>
                <IconComponent className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 text-left">{feature.title}</h3>
              <p className="text-sm text-gray-600 text-left mt-1">{feature.description}</p>
            </button>
          );
        })}
      </div>

      {/* Search Results */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {features.find(f => f.id === activeFeature)?.title || 'Search Results'}
          </h2>
          {searchResults.length > 0 && (
            <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
              {Array.isArray(searchResults[0]) || searchResults[0]?.category 
                ? searchResults.reduce((total, group) => total + (group.items?.length || 0), 0)
                : searchResults.length
              } results found
            </span>
          )}
        </div>
        
        {renderResults()}
      </div>

      {/* Technical Details */}
      <div className="mt-12 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔬 Technical Implementation</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Vector Search Features:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• CLIP-based multi-modal embeddings</li>
              <li>• Semantic similarity scoring</li>
              <li>• Style-preserving color mapping</li>
              <li>• Price-conscious alternative ranking</li>
              <li>• Seasonal trend analysis</li>
              <li>• Cross-category accessory matching</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">AI Capabilities:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Style transformation vectors</li>
              <li>• Compatibility scoring algorithms</li>
              <li>• Trend prediction models</li>
              <li>• Budget optimization search</li>
              <li>• Outfit completion suggestions</li>
              <li>• Real-time fashion analysis</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiModalSearchShowcase;
