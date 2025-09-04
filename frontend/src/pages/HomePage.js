import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Search, Sparkles } from 'lucide-react';
import ImageUpload from '../components/ImageUpload';
import SearchBar from '../components/SearchBar';
import { searchByImage, searchByText } from '../services/api';
import toast from 'react-hot-toast';

const HomePage = () => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  const categories = [
    'electronics', 'clothing', 'home', 'sports', 'books', 'beauty', 'automotive'
  ];

  const handleTextSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setIsSearching(true);
    try {
      const results = await searchByText(query, category);
      navigate('/search', { 
        state: { 
          results, 
          searchType: 'text', 
          query,
          category 
        } 
      });
    } catch (error) {
      toast.error('Search failed. Please try again.');
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleImageUpload = async (file) => {
    setIsUploading(true);
    try {
      const results = await searchByImage(file, category);
      navigate('/search', { 
        state: { 
          results, 
          searchType: 'image', 
          uploadedImage: URL.createObjectURL(file),
          category 
        } 
      });
    } catch (error) {
      toast.error('Image search failed. Please try again.');
      console.error('Image search error:', error);
    } finally {
      setIsUploading(false);
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

        {/* Search Interface */}
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Text Search */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <Search className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-semibold text-gray-900">
                Search by Text
              </h2>
            </div>
            
            <SearchBar
              query={query}
              setQuery={setQuery}
              onSearch={handleTextSearch}
              category={category}
              setCategory={setCategory}
              categories={categories}
              isLoading={isSearching}
            />
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-6 bg-gray-50 text-gray-500 font-medium">
                OR
              </span>
            </div>
          </div>

          {/* Image Search */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="flex items-center mb-6">
              <Camera className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-semibold text-gray-900">
                Search by Image
              </h2>
            </div>
            
            <ImageUpload 
              onImageUpload={handleImageUpload}
              isUploading={isUploading}
            />
          </div>
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
