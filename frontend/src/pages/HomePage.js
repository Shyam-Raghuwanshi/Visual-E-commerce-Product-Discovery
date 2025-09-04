import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Search, Sparkles } from 'lucide-react';
import MainSearchInterface from '../components/MainSearchInterface';
import useSearch from '../hooks/useSearch';

const HomePage = () => {
  const navigate = useNavigate();
  const { performSearch, isLoading } = useSearch();

  const handleSearch = async (searchParams) => {
    try {
      const results = await performSearch(searchParams);
      
      // Navigate to search results with all parameters
      navigate('/search', { 
        state: { 
          results, 
          searchParams,
          searchType: searchParams.mode,
          query: searchParams.query,
          uploadedImage: searchParams.image ? URL.createObjectURL(searchParams.image) : null,
          filters: searchParams.filters
        } 
      });
      
    } catch (error) {
      // Error handling is done in the hook
      console.error('Search error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="p-3 bg-blue-100 rounded-full">
              <Sparkles className="h-12 w-12 text-blue-600" />
            </div>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Visual Product
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {' '}Discovery
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Find products using the power of AI. Search with images, text, or combine both 
            for the most accurate results. Revolutionary e-commerce discovery at your fingertips.
          </p>
        </div>

        {/* Main Search Interface */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-16">
          <MainSearchInterface 
            onSearch={handleSearch}
            isLoading={isLoading}
          />
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Camera className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Image Recognition
            </h3>
            <p className="text-gray-600">
              Upload any product image and find similar items instantly using advanced AI vision technology.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Smart Text Search
            </h3>
            <p className="text-gray-600">
              Describe what you're looking for in natural language and get precisely relevant results.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              AI-Powered Matching
            </h3>
            <p className="text-gray-600">
              Combine multiple search methods for the most accurate product discovery experience.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
