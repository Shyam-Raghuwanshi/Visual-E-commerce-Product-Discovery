import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, Filter, SortAsc } from 'lucide-react';
import ProductGrid from '../components/ProductGrid';
import SearchBar from '../components/SearchBar';
import { searchByText } from '../services/api';

const SearchResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState(location.state?.results || null);
  const [query, setQuery] = useState(location.state?.query || '');
  const [category, setCategory] = useState(location.state?.category || '');
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState('relevance');
  
  const searchType = location.state?.searchType;
  const uploadedImage = location.state?.uploadedImage;

  const categories = [
    'electronics', 'clothing', 'home', 'sports', 'books', 'beauty', 'automotive'
  ];

  useEffect(() => {
    if (!results) {
      navigate('/');
    }
  }, [results, navigate]);

  const handleNewSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const newResults = await searchByText(query, category);
      setResults(newResults);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sortProducts = (products, scores) => {
    if (!products) return { products: [], scores: [] };

    const combined = products.map((product, index) => ({
      product,
      score: scores?.[index] || 0
    }));

    switch (sortBy) {
      case 'price-low':
        combined.sort((a, b) => a.product.price - b.product.price);
        break;
      case 'price-high':
        combined.sort((a, b) => b.product.price - a.product.price);
        break;
      case 'name':
        combined.sort((a, b) => a.product.name.localeCompare(b.product.name));
        break;
      default: // relevance
        combined.sort((a, b) => b.score - a.score);
    }

    return {
      products: combined.map(item => item.product),
      scores: combined.map(item => item.score)
    };
  };

  if (!results) {
    return null;
  }

  const { products: sortedProducts, scores: sortedScores } = sortProducts(
    results.products, 
    results.similarity_scores
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Search
          </button>

          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Search Results
              </h1>
              
              {searchType === 'image' && uploadedImage && (
                <div className="flex items-center space-x-4 mb-4">
                  <span className="text-gray-600">Searched with image:</span>
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded search" 
                    className="w-16 h-16 object-cover rounded-lg border"
                  />
                </div>
              )}
              
              {searchType === 'text' && query && (
                <p className="text-gray-600">
                  Results for: <span className="font-medium">"{query}"</span>
                </p>
              )}
              
              <p className="text-sm text-gray-500 mt-1">
                Found {results.total} products in {results.query_time?.toFixed(2) || 0}s
              </p>
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <SortAsc className="h-5 w-5 text-gray-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="relevance">Most Relevant</option>
                  <option value="price-low">Price: Low to High</option>
                  <option value="price-high">Price: High to Low</option>
                  <option value="name">Name A-Z</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Refine Search */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Refine your search
          </h2>
          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={handleNewSearch}
            category={category}
            setCategory={setCategory}
            categories={categories}
            isLoading={isLoading}
          />
        </div>

        {/* Results */}
        <ProductGrid
          products={sortedProducts}
          similarity_scores={sortedScores}
          loading={isLoading}
          error={null}
        />
      </div>
    </div>
  );
};

export default SearchResults;
