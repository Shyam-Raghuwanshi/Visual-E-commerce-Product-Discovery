import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, TrendingUp, Clock } from 'lucide-react';
import ProductGrid from '../components/ProductGrid';
import MainSearchInterface from '../components/MainSearchInterface';
import useSearch from '../hooks/useSearch';
import toast from 'react-hot-toast';

const SearchResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { performSearch, isLoading } = useSearch();
  
  const [results, setResults] = useState(location.state?.results || null);
  const [sortBy, setSortBy] = useState('relevance');
  const [showRefineSearch, setShowRefineSearch] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [allProducts, setAllProducts] = useState([]);
  const [allScores, setAllScores] = useState([]);
  const [hasMore, setHasMore] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  
  // Get initial search parameters
  const searchParams = location.state?.searchParams;
  const searchType = location.state?.searchType;
  const uploadedImage = location.state?.uploadedImage;
  const query = location.state?.query;
  const filters = location.state?.filters || {};

  // Initialize results
  useEffect(() => {
    if (!results) {
      navigate('/');
      return;
    }

    setAllProducts(results.products || []);
    setAllScores(results.similarity_scores || []);
    setTotalResults(results.total || 0);
    setHasMore((results.products?.length || 0) < (results.total || 0));
  }, [results, navigate]);

  // Handle refined search
  const handleRefineSearch = async (newSearchParams) => {
    try {
      const newResults = await performSearch(newSearchParams);
      setResults(newResults);
      setAllProducts(newResults.products || []);
      setAllScores(newResults.similarity_scores || []);
      setTotalResults(newResults.total || 0);
      setHasMore((newResults.products?.length || 0) < (newResults.total || 0));
      setCurrentPage(1);
      setShowRefineSearch(false);
      toast.success('Search refined successfully!');
    } catch (error) {
      console.error('Refine search error:', error);
    }
  };

  // Handle load more for infinite scroll
  const handleLoadMore = useCallback(async () => {
    if (!hasMore || isLoading) return;

    try {
      const nextPage = currentPage + 1;
      const loadMoreParams = {
        ...searchParams,
        page: nextPage,
        limit: 20
      };

      const moreResults = await performSearch(loadMoreParams);
      
      if (moreResults.products && moreResults.products.length > 0) {
        setAllProducts(prev => [...prev, ...moreResults.products]);
        setAllScores(prev => [...prev, ...(moreResults.similarity_scores || [])]);
        setCurrentPage(nextPage);
        setHasMore(allProducts.length + moreResults.products.length < totalResults);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Load more error:', error);
      toast.error('Failed to load more products');
    }
  }, [hasMore, isLoading, currentPage, searchParams, performSearch, allProducts.length, totalResults]);

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    // Here you could also trigger a new search with the sort parameter
  };

  // Handle view mode change
  const handleViewModeChange = (newViewMode) => {
    // In a real app, this might update URL params or trigger re-fetch
    console.log('View mode changed to:', newViewMode);
  };

  // Sort products locally (in a real app, this might be done server-side)
  const sortProducts = (products, scores) => {
    if (!products) return { products: [], scores: [] };

    const combined = products.map((product, index) => ({
      product,
      score: scores?.[index] || 0
    }));

    switch (sortBy) {
      case 'price_low':
        combined.sort((a, b) => a.product.price - b.product.price);
        break;
      case 'price_high':
        combined.sort((a, b) => b.product.price - a.product.price);
        break;
      case 'rating':
        combined.sort((a, b) => (b.product.rating || 0) - (a.product.rating || 0));
        break;
      case 'newest':
        combined.sort((a, b) => new Date(b.product.created_at || 0) - new Date(a.product.created_at || 0));
        break;
      case 'popular':
        combined.sort((a, b) => (b.product.view_count || 0) - (a.product.view_count || 0));
        break;
      default: // relevance
        combined.sort((a, b) => b.score - a.score);
    }

    return {
      products: combined.map(item => item.product),
      scores: combined.map(item => item.score)
    };
  };

  // Generate explanations for why products match
  const generateExplanations = (products, searchParams) => {
    const explanations = {};
    
    products.forEach(product => {
      const reasons = [];
      
      if (searchParams.query) {
        if (product.name.toLowerCase().includes(searchParams.query.toLowerCase())) {
          reasons.push("Title contains search terms");
        }
        if (product.description && product.description.toLowerCase().includes(searchParams.query.toLowerCase())) {
          reasons.push("Description matches");
        }
        if (product.category && product.category.toLowerCase().includes(searchParams.query.toLowerCase())) {
          reasons.push("Category matches");
        }
      }
      
      if (product.rating && product.rating > 4.0) {
        reasons.push("Highly rated product");
      }
      
      if (product.brand && filters.brands?.includes(product.brand)) {
        reasons.push("Matches selected brand");
      }
      
      if (product.category && filters.categories?.includes(product.category)) {
        reasons.push("Matches selected category");
      }
      
      if (reasons.length === 0) {
        reasons.push("Visual similarity to search criteria");
      }
      
      explanations[product.id] = reasons.join(" • ");
    });
    
    return explanations;
  };

  if (!results) {
    return null;
  }

  const { products: sortedProducts, scores: sortedScores } = sortProducts(
    allProducts, 
    allScores
  );

  const explanations = generateExplanations(sortedProducts, searchParams);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Search
          </button>

          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                  Search Results
                </h1>
                
                {/* Search Type and Query Display */}
                <div className="flex flex-wrap items-center gap-3 mb-4">
                  <span className={`
                    px-3 py-1 rounded-full text-sm font-medium
                    ${searchType === 'text' ? 'bg-blue-100 text-blue-800' : ''}
                    ${searchType === 'image' ? 'bg-purple-100 text-purple-800' : ''}
                    ${searchType === 'hybrid' ? 'bg-green-100 text-green-800' : ''}
                  `}>
                    {searchType === 'text' && '🔤 Text Search'}
                    {searchType === 'image' && '📷 Image Search'}
                  </span>
                  
                  {searchType === 'text' && query && (
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600 text-sm">Query:</span>
                      <span className="font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                        "{query}"
                      </span>
                    </div>
                  )}
                  
                  {(searchType === 'image' || searchType === 'hybrid') && uploadedImage && (
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600 text-sm">Image:</span>
                      <img 
                        src={uploadedImage} 
                        alt="Search reference" 
                        className="w-12 h-12 object-cover rounded-lg border-2 border-gray-200"
                      />
                    </div>
                  )}
                </div>
                
                {/* Applied Filters */}
                {(filters.categories?.length > 0 || filters.brands?.length > 0 || filters.priceRange || filters.minPrice || filters.maxPrice) && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="text-sm text-gray-500 flex items-center">
                      🔍 Active Filters:
                    </span>
                    {filters.categories?.map(cat => (
                      <span key={cat} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        📂 {cat}
                      </span>
                    ))}
                    {filters.brands?.map(brand => (
                      <span key={brand} className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                        🏷️ {brand}
                      </span>
                    ))}
                    {filters.priceRange && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                        💰 {filters.priceRange.label}
                      </span>
                    )}
                    {(filters.minPrice || filters.maxPrice) && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                        💰 ${filters.minPrice || 0} - ${filters.maxPrice || '∞'}
                      </span>
                    )}
                    {filters.inStockOnly && (
                      <span className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
                        📦 In Stock Only
                      </span>
                    )}
                    {filters.minRating > 0 && (
                      <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                        ⭐ {filters.minRating}+ Stars
                      </span>
                    )}
                  </div>
                )}
                
                {/* Results Summary */}
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>{totalResults.toLocaleString()} products found</span>
                  </div>
                  {results.query_time && (
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>in {results.query_time.toFixed(3)}s</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <div className="flex-shrink-0">
                <button
                  onClick={() => setShowRefineSearch(!showRefineSearch)}
                  className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refine Search
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Refine Search Panel */}
        {showRefineSearch && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                🔧 Refine Your Search
              </h2>
              <button
                onClick={() => setShowRefineSearch(false)}
                className="text-gray-400 hover:text-gray-600 text-xl font-bold"
              >
                ✕
              </button>
            </div>
            <MainSearchInterface
              onSearch={handleRefineSearch}
              isLoading={isLoading}
              initialQuery={query || ''}
              initialFilters={filters}
            />
          </div>
        )}

        {/* Enhanced Product Grid */}
        <ProductGrid
          products={sortedProducts}
          similarity_scores={sortedScores}
          loading={isLoading}
          error={null}
          searchParams={searchParams}
          onLoadMore={handleLoadMore}
          hasMore={hasMore}
          totalResults={totalResults}
          currentPage={currentPage}
          onSortChange={handleSortChange}
          onViewModeChange={handleViewModeChange}
          explanations={explanations}
        />

        {/* Performance Metrics */}
        {results.query_time && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white rounded-lg shadow-sm border border-gray-200">
              <Clock className="w-4 h-4 text-gray-500 mr-2" />
              <span className="text-sm text-gray-600">
                Search completed in {results.query_time.toFixed(3)} seconds
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResults;
