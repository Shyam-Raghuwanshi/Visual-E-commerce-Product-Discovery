import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Grid, 
  List, 
  ChevronDown, 
  Filter,
  SortAsc,
  SortDesc,
  Loader2,
  AlertCircle,
  Search,
  Star,
  TrendingUp,
  Clock,
  Zap,
  Settings,
  Sliders,
  Share2
} from 'lucide-react';
import ProductCard from './ProductCard';
import AdvancedSearchInterface from './AdvancedSearchInterface';

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Most Relevant', icon: Zap },
  { value: 'price_low', label: 'Price: Low to High', icon: SortAsc },
  { value: 'price_high', label: 'Price: High to Low', icon: SortDesc },
  { value: 'newest', label: 'Newest First', icon: Clock },
  { value: 'rating', label: 'Highest Rated', icon: Star },
  { value: 'popular', label: 'Most Popular', icon: TrendingUp }
];

const VIEW_MODES = {
  GRID: 'grid',
  LIST: 'list'
};

const ProductGrid = ({ 
  products = [], 
  loading = false, 
  error = null, 
  similarity_scores = [],
  searchParams = {},
  onLoadMore = null,
  hasMore = false,
  totalResults = 0,
  currentPage = 1,
  onSortChange = null,
  onViewModeChange = null,
  explanations = {},
  showAdvancedFeatures = false,
  onAdvancedSearch = () => {},
  onStyleTransfer = () => {},
  onOutfitSearch = () => {}
}) => {
  const [viewMode, setViewMode] = useState(VIEW_MODES.GRID);
  const [sortBy, setSortBy] = useState('relevance');
  const [showSortDropdown, setShowSortDropdown] = useState(false);
  const [savedProducts, setSavedProducts] = useState(new Set());
  const [loadingMore, setLoadingMore] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(showAdvancedFeatures);
  
  const loadMoreRef = useRef();
  const sortDropdownRef = useRef();

  // Handle infinite scroll
  const handleLoadMore = useCallback(async () => {
    if (hasMore && !loadingMore && onLoadMore) {
      setLoadingMore(true);
      try {
        await onLoadMore();
      } finally {
        setLoadingMore(false);
      }
    }
  }, [hasMore, loadingMore, onLoadMore]);

  // Intersection Observer for infinite scroll
  useEffect(() => {
    const currentRef = loadMoreRef.current;
    
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          handleLoadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [handleLoadMore]);

  // Close sort dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sortDropdownRef.current && !sortDropdownRef.current.contains(event.target)) {
        setShowSortDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    setShowSortDropdown(false);
    if (onSortChange) {
      onSortChange(newSortBy);
    }
  };

  // Handle view mode change
  const handleViewModeChange = (newViewMode) => {
    setViewMode(newViewMode);
    if (onViewModeChange) {
      onViewModeChange(newViewMode);
    }
  };

  // Handle save/unsave product
  const handleSaveProduct = (productId) => {
    const newSavedProducts = new Set(savedProducts);
    if (newSavedProducts.has(productId)) {
      newSavedProducts.delete(productId);
    } else {
      newSavedProducts.add(productId);
    }
    setSavedProducts(newSavedProducts);
  };

  // Handle share product
  const handleShareProduct = async (product) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: product.name,
          text: `Check out this product: ${product.name}`,
          url: window.location.href
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      // You could show a toast notification here
    }
  };

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className={`grid gap-6 ${
      viewMode === VIEW_MODES.GRID 
        ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
        : 'grid-cols-1'
    }`}>
      {[...Array(8)].map((_, index) => (
        <div 
          key={index} 
          className={`bg-white rounded-lg shadow-sm animate-pulse ${
            viewMode === VIEW_MODES.LIST ? 'flex space-x-4 p-4' : ''
          }`}
        >
          <div className={`bg-gray-200 rounded-lg ${
            viewMode === VIEW_MODES.LIST 
              ? 'w-32 h-32 flex-shrink-0' 
              : 'aspect-square rounded-t-lg'
          }`}></div>
          <div className={`p-4 space-y-3 ${viewMode === VIEW_MODES.LIST ? 'flex-1' : ''}`}>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      ))}
    </div>
  );

  // Error state
  if (error) {
    return (
      <div className="text-center py-16">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Error loading products</h3>
        <p className="text-gray-600 mb-6">{error.message || 'Something went wrong while loading products.'}</p>
        <button 
          onClick={() => window.location.reload()}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Empty state
  if (!loading && (!products || products.length === 0)) {
    return (
      <div className="text-center py-16">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          <Search className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No products found</h3>
        <p className="text-gray-600 mb-6">
          We couldn't find any products matching your search criteria.
        </p>
        <div className="space-y-2 text-sm text-gray-500">
          <p>Try:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Using different keywords</li>
            <li>Checking your spelling</li>
            <li>Using more general terms</li>
            <li>Uploading a different image</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Advanced Search Interface */}
      {showAdvanced && (
        <AdvancedSearchInterface
          searchResults={products}
          currentProduct={products[0]} // Use first product as example
          onAdvancedSearch={onAdvancedSearch}
          onStyleTransfer={onStyleTransfer}
          onOutfitSearch={onOutfitSearch}
          loading={loading}
        />
      )}

      {/* Results Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center space-x-4">
          <div>
            <p className="text-sm text-gray-600">
              {loading ? 'Searching...' : `${totalResults.toLocaleString()} results found`}
            </p>
            {searchParams.query && (
              <p className="text-xs text-gray-500 mt-1">
                for "{searchParams.query}"
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Advanced Features Toggle */}
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`flex items-center space-x-2 px-3 py-2 border rounded-lg text-sm transition-colors ${
              showAdvanced 
                ? 'border-blue-300 bg-blue-50 text-blue-700' 
                : 'border-gray-300 hover:bg-gray-50 text-gray-600'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>Advanced</span>
          </button>

          {/* Sort Dropdown */}
          <div className="relative" ref={sortDropdownRef}>
            <button
              onClick={() => setShowSortDropdown(!showSortDropdown)}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
            >
              <Filter className="w-4 h-4" />
              <span>Sort: {SORT_OPTIONS.find(option => option.value === sortBy)?.label}</span>
              <ChevronDown className="w-4 h-4" />
            </button>

            {showSortDropdown && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="py-1">
                  {SORT_OPTIONS.map((option) => {
                    const Icon = option.icon;
                    return (
                      <button
                        key={option.value}
                        onClick={() => handleSortChange(option.value)}
                        className={`w-full flex items-center space-x-3 px-4 py-2 text-sm text-left hover:bg-gray-50 transition-colors ${
                          sortBy === option.value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{option.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => handleViewModeChange(VIEW_MODES.GRID)}
              className={`p-2 ${
                viewMode === VIEW_MODES.GRID 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              } transition-colors`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleViewModeChange(VIEW_MODES.LIST)}
              className={`p-2 ${
                viewMode === VIEW_MODES.LIST 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              } transition-colors`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && products.length === 0 && <LoadingSkeleton />}

      {/* Products Grid */}
      {!loading && products.length > 0 && (
        <div className={`grid gap-6 ${
          viewMode === VIEW_MODES.GRID 
            ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
            : 'grid-cols-1'
        }`}>
          {products.map((product, index) => (
            <ProductCard
              key={product.id || index}
              product={product}
              similarity_score={similarity_scores[index]}
              viewMode={viewMode}
              isSaved={savedProducts.has(product.id)}
              onSave={() => handleSaveProduct(product.id)}
              onShare={() => handleShareProduct(product)}
              explanation={explanations[product.id]}
              searchParams={searchParams}
            />
          ))}
        </div>
      )}

      {/* Load More / Pagination */}
      {!loading && products.length > 0 && hasMore && (
        <div ref={loadMoreRef} className="flex justify-center py-8">
          {loadingMore ? (
            <div className="flex items-center space-x-2 text-gray-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading more products...</span>
            </div>
          ) : (
            <button
              onClick={handleLoadMore}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Load More Products
            </button>
          )}
        </div>
      )}

      {/* Results Footer */}
      {!loading && products.length > 0 && !hasMore && (
        <div className="text-center py-8 text-gray-500">
          <p>You've seen all {totalResults.toLocaleString()} results</p>
        </div>
      )}
    </div>
  );
};

export default ProductGrid;
