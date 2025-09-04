import React, { useState } from 'react';
import { Settings, Sparkles } from 'lucide-react';
import ProductGrid from '../components/ProductGrid';
import {
  VisualSimilaritySlider,
  StyleTransferInterface,
  OutfitBuilder,
  PriceComparison,
  SearchHistory,
  SocialSharing
} from '../components/advanced';

const ExampleAdvancedSearchPage = () => {
  const [searchResults, setSearchResults] = useState([
    {
      id: 1,
      name: "Summer Floral Dress",
      price: 89.99,
      originalPrice: 129.99,
      image_url: "/api/placeholder/300/300",
      brand: "Fashion Brand",
      rating: 4.5,
      reviewCount: 128
    },
    {
      id: 2,
      name: "Casual Blue Jeans",
      price: 59.99,
      image_url: "/api/placeholder/300/300",
      brand: "Denim Co",
      rating: 4.2,
      reviewCount: 89
    }
  ]);

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [currentSearchImage, setCurrentSearchImage] = useState(null);

  // Handler functions for advanced features
  const handleAdvancedSearch = (params) => {
    console.log('Advanced search params:', params);
    // Implement your advanced search logic here
  };

  const handleStyleTransfer = (styleParams) => {
    console.log('Style transfer params:', styleParams);
    // Implement style transfer search logic
  };

  const handleOutfitSearch = (outfitParams) => {
    console.log('Outfit search params:', outfitParams);
    // Implement outfit-based search logic
  };

  const handleCreateWishlist = (wishlist) => {
    console.log('Creating wishlist:', wishlist);
    // Save wishlist to backend
  };

  const handleCreateCollection = (collection) => {
    console.log('Creating collection:', collection);
    // Save collection to backend
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Advanced Product Search
            </h1>
            <p className="text-gray-600 mt-2">
              AI-powered search tools for better product discovery
            </p>
          </div>
          
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
              showAdvanced 
                ? 'bg-blue-600 text-white border-blue-600' 
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Tools</span>
          </button>
        </div>

        {/* Advanced Tools Section */}
        {showAdvanced && (
          <div className="space-y-8 mb-8">
            {/* Visual Similarity Slider */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                Search Balance Control
              </h2>
              <VisualSimilaritySlider
                imageWeight={0.7}
                textWeight={0.3}
                onChange={handleAdvancedSearch}
              />
            </section>

            {/* Style Transfer */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                Style Transfer
              </h2>
              <StyleTransferInterface
                originalImage={currentSearchImage}
                onStyleTransfer={handleStyleTransfer}
              />
            </section>

            {/* Outfit Builder */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-green-600" />
                Outfit Builder
              </h2>
              <OutfitBuilder
                onOutfitSearch={handleOutfitSearch}
                onSaveOutfit={(outfit) => console.log('Save outfit:', outfit)}
                onShareOutfit={(outfit) => console.log('Share outfit:', outfit)}
              />
            </section>

            {/* Price Comparison */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-orange-600" />
                Price Comparison
              </h2>
              <PriceComparison
                product={searchResults[0]}
                alternatives={searchResults.slice(1)}
                onAddToCart={(product) => console.log('Add to cart:', product)}
                onSaveProduct={(id) => console.log('Save product:', id)}
              />
            </section>

            {/* Search History */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-indigo-600" />
                Search History
              </h2>
              <SearchHistory
                onSearchFromHistory={handleAdvancedSearch}
                onSaveSearch={(search) => console.log('Save search:', search)}
                onLoadSavedSearch={handleAdvancedSearch}
              />
            </section>

            {/* Social Sharing */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-pink-600" />
                Social Sharing
              </h2>
              <SocialSharing
                searchResults={searchResults}
                searchQuery="summer fashion"
                searchType="text"
                onCreateWishlist={handleCreateWishlist}
                onCreateCollection={handleCreateCollection}
              />
            </section>
          </div>
        )}

        {/* Product Grid with Advanced Features */}
        <ProductGrid
          products={searchResults}
          showAdvancedFeatures={showAdvanced}
          onAdvancedSearch={handleAdvancedSearch}
          onStyleTransfer={handleStyleTransfer}
          onOutfitSearch={handleOutfitSearch}
          totalResults={searchResults.length}
          loading={false}
          searchParams={{ query: 'summer fashion' }}
        />
      </div>
    </div>
  );
};

export default ExampleAdvancedSearchPage;
