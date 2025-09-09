import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Search, 
  X, 
  ChevronDown, 
  Image as ImageIcon,
  Sliders,
  RotateCcw,
  Camera,
  Type,
  Combine,
  Star,
  DollarSign,
  Tag,
  Building2,
  Loader2
} from 'lucide-react';
import { useQuery } from 'react-query';
import { getCategories } from '../services/api';
import toast from 'react-hot-toast';

const SEARCH_MODES = {
  TEXT: 'text',
  IMAGE: 'image',
  HYBRID: 'hybrid'
};

const PRICE_RANGES = [
  { label: 'Under $50', min: 0, max: 50 },
  { label: '$50 - $100', min: 50, max: 100 },
  { label: '$100 - $250', min: 100, max: 250 },
  { label: '$250 - $500', min: 250, max: 500 },
  { label: '$500+', min: 500, max: null }
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Most Relevant' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'newest', label: 'Newest First' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'popular', label: 'Most Popular' }
];

const MainSearchInterface = ({ 
  onSearch, 
  isLoading = false,
  initialQuery = '',
  initialFilters = {}
}) => {
  // Search state
  const [searchMode, setSearchMode] = useState(SEARCH_MODES.TEXT);
  const [textQuery, setTextQuery] = useState(initialQuery);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  
  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState(initialFilters.categories || []);
  const [selectedBrands, setSelectedBrands] = useState(initialFilters.brands || []);
  const [priceRange, setPriceRange] = useState(initialFilters.priceRange || null);
  const [minPrice, setMinPrice] = useState(initialFilters.minPrice || '');
  const [maxPrice, setMaxPrice] = useState(initialFilters.maxPrice || '');
  const [sortBy, setSortBy] = useState(initialFilters.sortBy || 'relevance');
  const [inStockOnly, setInStockOnly] = useState(initialFilters.inStockOnly || false);
  const [minRating, setMinRating] = useState(initialFilters.minRating || 0);
  
  // Autocomplete state
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  
  // Load categories
  const { data: categories = [], isLoading: categoriesLoading } = useQuery(
    'categories',
    getCategories,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      onError: (error) => {
        console.error('Failed to load categories:', error);
      }
    }
  );

  // Mock brands - in real app, this would come from API
  const brands = useMemo(() => [
    'Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'LG', 'Canon', 'Nikon',
    'Dell', 'HP', 'Lenovo', 'ASUS', 'Microsoft', 'Google', 'Amazon'
  ], []);

  // Image upload handling
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('Image size must be less than 10MB');
        return;
      }
      
      setSelectedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
      
      // Auto-switch to image or hybrid mode
      if (searchMode === SEARCH_MODES.TEXT && !textQuery.trim()) {
        setSearchMode(SEARCH_MODES.IMAGE);
      } else if (searchMode === SEARCH_MODES.TEXT && textQuery.trim()) {
        setSearchMode(SEARCH_MODES.HYBRID);
      }
    }
  }, [searchMode, textQuery]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.gif']
    },
    multiple: false,
    disabled: isLoading,
    noClick: searchMode === SEARCH_MODES.TEXT
  });

  // Handle search mode changes
  const handleModeChange = (mode) => {
    setSearchMode(mode);
    
    // Clear incompatible data
    if (mode === SEARCH_MODES.TEXT) {
      setSelectedImage(null);
      setImagePreview(null);
    }
  };

  // Remove uploaded image
  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    
    // Switch back to text mode if no text query
    if (searchMode === SEARCH_MODES.HYBRID && !textQuery.trim()) {
      setSearchMode(SEARCH_MODES.TEXT);
    } else if (searchMode === SEARCH_MODES.IMAGE) {
      setSearchMode(SEARCH_MODES.TEXT);
    }
  };

  // Handle search submission
  const handleSearch = (e) => {
    e?.preventDefault();
    
    // Validate inputs
    const hasTextQuery = textQuery.trim().length > 0;
    const hasImage = selectedImage !== null;
    
    if (!hasTextQuery && !hasImage) {
      toast.error('Please enter a search query or upload an image');
      return;
    }

    if (searchMode === SEARCH_MODES.TEXT && !hasTextQuery) {
      toast.error('Please enter a search query');
      return;
    }

    if (searchMode === SEARCH_MODES.IMAGE && !hasImage) {
      toast.error('Please upload an image');
      return;
    }

    

    // Build search parameters
    const searchParams = {
      mode: searchMode,
      query: hasTextQuery ? textQuery.trim() : null,
      image: hasImage ? selectedImage : null,
      filters: {
        categories: selectedCategories,
        brands: selectedBrands,
        priceRange: priceRange,
        minPrice: minPrice ? parseFloat(minPrice) : null,
        maxPrice: maxPrice ? parseFloat(maxPrice) : null,
        sortBy,
        inStockOnly,
        minRating: minRating > 0 ? minRating : null
      }
    };

    onSearch(searchParams);
    setShowAutocomplete(false);
  };

  // Clear all filters
  const clearFilters = () => {
    setSelectedCategories([]);
    setSelectedBrands([]);
    setPriceRange(null);
    setMinPrice('');
    setMaxPrice('');
    setSortBy('relevance');
    setInStockOnly(false);
    setMinRating(0);
  };

  // Mock autocomplete suggestions
  useEffect(() => {
    if (textQuery.length > 2) {
      const mockSuggestions = [
        `${textQuery} phone`,
        `${textQuery} laptop`,
        `${textQuery} headphones`,
        `${textQuery} camera`,
        `${textQuery} watch`
      ].slice(0, 5);
      setSuggestions(mockSuggestions);
    } else {
      setSuggestions([]);
    }
  }, [textQuery]);

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (selectedCategories.length > 0) count++;
    if (selectedBrands.length > 0) count++;
    if (priceRange || minPrice || maxPrice) count++;
    if (inStockOnly) count++;
    if (minRating > 0) count++;
    return count;
  }, [selectedCategories, selectedBrands, priceRange, minPrice, maxPrice, inStockOnly, minRating]);

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-6">
      {/* Search Mode Toggle */}
      <div className="flex justify-center">
        <div className="inline-flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => handleModeChange(SEARCH_MODES.TEXT)}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              searchMode === SEARCH_MODES.TEXT
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Type className="w-4 h-4 mr-2" />
            Text Search
          </button>
          <button
            onClick={() => handleModeChange(SEARCH_MODES.IMAGE)}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              searchMode === SEARCH_MODES.IMAGE
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Camera className="w-4 h-4 mr-2" />
            Image Search
          </button>
        </div>
      </div>

      {/* Main Search Interface */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Text Search Section */}
          {(searchMode === SEARCH_MODES.TEXT || searchMode === SEARCH_MODES.HYBRID) && (
            <div className="flex-1 space-y-2">
              <div className="relative">
                <input
                  type="text"
                  value={textQuery}
                  onChange={(e) => {
                    setTextQuery(e.target.value);
                    setShowAutocomplete(true);
                  }}
                  onFocus={() => setShowAutocomplete(suggestions.length > 0)}
                  onBlur={() => setTimeout(() => setShowAutocomplete(false), 200)}
                  placeholder={
                    searchMode === SEARCH_MODES.HYBRID 
                      ? "Describe what you're looking for..." 
                      : "Search for products..."
                  }
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  required={searchMode === SEARCH_MODES.TEXT}
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                
                {/* Autocomplete Dropdown */}
                {showAutocomplete && suggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => {
                          setTextQuery(suggestion);
                          setShowAutocomplete(false);
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Image Upload Section */}
          {(searchMode === SEARCH_MODES.IMAGE || searchMode === SEARCH_MODES.HYBRID) && (
            <div className="flex-1">
              {imagePreview ? (
                <div className="relative">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                    <div className="flex items-center space-x-4">
                      <img
                        src={imagePreview}
                        alt="Upload preview"
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {selectedImage?.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(selectedImage?.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={removeImage}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  {...getRootProps()}
                  className={`
                    border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
                    ${isDragActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                    }
                    ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <input {...getInputProps()} />
                  <div className="space-y-2">
                    {isLoading ? (
                      <Loader2 className="w-8 h-8 mx-auto text-blue-500 animate-spin" />
                    ) : (
                      <ImageIcon className="w-8 h-8 mx-auto text-gray-400" />
                    )}
                    
                    {isDragActive ? (
                      <p className="text-blue-600 font-medium">Drop the image here...</p>
                    ) : (
                      <div>
                        <p className="text-gray-600">
                          <span className="font-medium">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-gray-500">
                          PNG, JPG, WEBP up to 10MB
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Search Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Filters Toggle */}
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`
              flex items-center justify-center px-4 py-2 border rounded-lg text-sm font-medium transition-colors
              ${showFilters 
                ? 'bg-blue-50 border-blue-200 text-blue-700' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }
            `}
          >
            <Sliders className="w-4 h-4 mr-2" />
            Filters
            {activeFiltersCount > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                {activeFiltersCount}
              </span>
            )}
          </button>

          {/* Sort Dropdown */}
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={isLoading || (!textQuery.trim() && !selectedImage)}
            className="flex-1 sm:flex-none px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <Search className="w-4 h-4" />
                <span>Search</span>
              </div>
            )}
          </button>
        </div>
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFilters}
                className="flex items-center text-sm text-blue-600 hover:text-blue-700"
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                Clear All
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Categories Filter */}
            <div className="space-y-3">
              <div className="flex items-center">
                <Tag className="w-4 h-4 mr-2 text-gray-500" />
                <label className="text-sm font-medium text-gray-700">Categories</label>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {categoriesLoading ? (
                  <div className="text-sm text-gray-500">Loading...</div>
                ) : (
                  categories.map((category) => (
                    <label key={category} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCategories.includes(category)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCategories([...selectedCategories, category]);
                          } else {
                            setSelectedCategories(selectedCategories.filter(c => c !== category));
                          }
                        }}
                        className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700 capitalize">{category}</span>
                    </label>
                  ))
                )}
              </div>
            </div>

            {/* Brands Filter */}
            <div className="space-y-3">
              <div className="flex items-center">
                <Building2 className="w-4 h-4 mr-2 text-gray-500" />
                <label className="text-sm font-medium text-gray-700">Brands</label>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {brands.map((brand) => (
                  <label key={brand} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedBrands.includes(brand)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedBrands([...selectedBrands, brand]);
                        } else {
                          setSelectedBrands(selectedBrands.filter(b => b !== brand));
                        }
                      }}
                      className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{brand}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Price Filter */}
            <div className="space-y-3">
              <div className="flex items-center">
                <DollarSign className="w-4 h-4 mr-2 text-gray-500" />
                <label className="text-sm font-medium text-gray-700">Price Range</label>
              </div>
              
              {/* Quick Price Ranges */}
              <div className="space-y-2">
                {PRICE_RANGES.map((range, index) => (
                  <label key={index} className="flex items-center">
                    <input
                      type="radio"
                      name="priceRange"
                      checked={priceRange === range}
                      onChange={() => {
                        setPriceRange(range);
                        setMinPrice('');
                        setMaxPrice('');
                      }}
                      className="mr-2 border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{range.label}</span>
                  </label>
                ))}
              </div>

              {/* Custom Price Range */}
              <div className="pt-2 border-t border-gray-200">
                <label className="flex items-center mb-2">
                  <input
                    type="radio"
                    name="priceRange"
                    checked={!priceRange && (minPrice || maxPrice)}
                    onChange={() => setPriceRange(null)}
                    className="mr-2 border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Custom Range</span>
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={minPrice}
                    onChange={(e) => {
                      setMinPrice(e.target.value);
                      if (e.target.value || maxPrice) {
                        setPriceRange(null);
                      }
                    }}
                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={maxPrice}
                    onChange={(e) => {
                      setMaxPrice(e.target.value);
                      if (e.target.value || minPrice) {
                        setPriceRange(null);
                      }
                    }}
                    className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Additional Filters */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-700">Additional Filters</label>
              
              {/* In Stock Only */}
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={inStockOnly}
                  onChange={(e) => setInStockOnly(e.target.checked)}
                  className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">In Stock Only</span>
              </label>

              {/* Minimum Rating */}
              <div className="space-y-2">
                <label className="text-sm text-gray-700">Minimum Rating</label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      type="button"
                      onClick={() => setMinRating(rating === minRating ? 0 : rating)}
                      className={`p-1 rounded ${
                        rating <= minRating 
                          ? 'text-yellow-400' 
                          : 'text-gray-300 hover:text-gray-400'
                      }`}
                    >
                      <Star className="w-4 h-4 fill-current" />
                    </button>
                  ))}
                  {minRating > 0 && (
                    <span className="text-xs text-gray-600">{minRating}+ stars</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainSearchInterface;
