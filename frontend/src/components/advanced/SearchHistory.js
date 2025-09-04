import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Search, 
  Heart, 
  X,
  ArrowRight,
  Star,
  Trash2,
  Edit,
  FolderPlus,
  Filter,
  Calendar,
  TrendingUp,
  Eye,
  Download,
  Bookmark
} from 'lucide-react';

const SearchHistory = ({ 
  onSearchFromHistory = () => {},
  onSaveSearch = () => {},
  onLoadSavedSearch = () => {},
  maxHistoryItems = 50,
  maxSavedSearches = 20
}) => {
  const [searchHistory, setSearchHistory] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [activeTab, setActiveTab] = useState('history'); // 'history', 'saved'
  const [filterType, setFilterType] = useState('all'); // 'all', 'text', 'image', 'advanced'
  const [searchTerm, setSearchTerm] = useState('');
  const [editingSearch, setEditingSearch] = useState(null);
  const [newSearchName, setNewSearchName] = useState('');

  // Load data from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    const savedSearchesList = localStorage.getItem('savedSearches');
    
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
    
    if (savedSearchesList) {
      setSavedSearches(JSON.parse(savedSearchesList));
    }
  }, []);

  // Save to localStorage when data changes
  useEffect(() => {
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
  }, [searchHistory]);

  useEffect(() => {
    localStorage.setItem('savedSearches', JSON.stringify(savedSearches));
  }, [savedSearches]);

  // Add search to history
  const addToHistory = (searchData) => {
    const newHistoryItem = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      query: searchData.query || '',
      type: searchData.type || 'text', // 'text', 'image', 'advanced'
      filters: searchData.filters || {},
      resultsCount: searchData.resultsCount || 0,
      imageUrl: searchData.imageUrl || null
    };

    setSearchHistory(prev => {
      // Remove duplicate if exists
      const filtered = prev.filter(item => 
        !(item.query === newHistoryItem.query && 
          item.type === newHistoryItem.type &&
          JSON.stringify(item.filters) === JSON.stringify(newHistoryItem.filters))
      );
      
      // Add to beginning and limit size
      return [newHistoryItem, ...filtered].slice(0, maxHistoryItems);
    });
  };

  // Remove from history
  const removeFromHistory = (id) => {
    setSearchHistory(prev => prev.filter(item => item.id !== id));
  };

  // Clear all history
  const clearHistory = () => {
    setSearchHistory([]);
  };

  // Save search
  const saveSearch = (historyItem, customName = '') => {
    const savedSearch = {
      ...historyItem,
      savedId: Date.now(),
      savedAt: new Date().toISOString(),
      name: customName || historyItem.query || 'Unnamed Search',
      category: 'general'
    };

    setSavedSearches(prev => {
      // Check if already saved
      const exists = prev.some(saved => 
        saved.query === savedSearch.query && 
        saved.type === savedSearch.type &&
        JSON.stringify(saved.filters) === JSON.stringify(savedSearch.filters)
      );
      
      if (exists) return prev;
      
      return [savedSearch, ...prev].slice(0, maxSavedSearches);
    });
  };

  // Remove saved search
  const removeSavedSearch = (savedId) => {
    setSavedSearches(prev => prev.filter(item => item.savedId !== savedId));
  };

  // Update saved search name
  const updateSavedSearchName = (savedId, newName) => {
    setSavedSearches(prev => 
      prev.map(item => 
        item.savedId === savedId 
          ? { ...item, name: newName }
          : item
      )
    );
    setEditingSearch(null);
    setNewSearchName('');
  };

  // Filter searches
  const filterSearches = (searches) => {
    let filtered = searches;

    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(item => item.type === filterType);
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.name && item.name.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    return filtered;
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get search type icon
  const getSearchTypeIcon = (type) => {
    switch (type) {
      case 'image':
        return '🖼️';
      case 'advanced':
        return '⚙️';
      case 'text':
      default:
        return '🔍';
    }
  };

  // Export searches
  const exportSearches = () => {
    const data = {
      searchHistory,
      savedSearches,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'search-history.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredHistory = filterSearches(searchHistory);
  const filteredSaved = filterSearches(savedSearches);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Clock className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Search History</h3>
        </div>
        
        <button
          onClick={exportSearches}
          className="flex items-center space-x-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Export</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'history'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Recent ({searchHistory.length})</span>
        </button>
        
        <button
          onClick={() => setActiveTab('saved')}
          className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'saved'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Bookmark className="w-4 h-4" />
          <span>Saved ({savedSearches.length})</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search your history..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="text">Text Search</option>
            <option value="image">Image Search</option>
            <option value="advanced">Advanced Search</option>
          </select>
        </div>
      </div>

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-4">
          {/* Clear History Button */}
          {searchHistory.length > 0 && (
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                {filteredHistory.length} of {searchHistory.length} searches
              </p>
              <button
                onClick={clearHistory}
                className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:text-red-800 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear All</span>
              </button>
            </div>
          )}

          {/* History List */}
          {filteredHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-8 h-8 mx-auto mb-2" />
              <p>No search history found</p>
              {searchTerm && <p className="text-sm mt-1">Try adjusting your filters</p>}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredHistory.map((item) => (
                <div
                  key={item.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-lg">{getSearchTypeIcon(item.type)}</span>
                        <span className="text-sm font-medium text-gray-900">
                          {item.query || 'Image Search'}
                        </span>
                        <span className="text-xs text-gray-500 capitalize">
                          {item.type}
                        </span>
                      </div>
                      
                      {item.imageUrl && (
                        <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden mb-2">
                          <img 
                            src={item.imageUrl} 
                            alt="Search" 
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatTimestamp(item.timestamp)}</span>
                        </span>
                        {item.resultsCount > 0 && (
                          <span className="flex items-center space-x-1">
                            <TrendingUp className="w-3 h-3" />
                            <span>{item.resultsCount} results</span>
                          </span>
                        )}
                      </div>
                      
                      {Object.keys(item.filters || {}).length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {Object.entries(item.filters).map(([key, value]) => (
                            <span
                              key={key}
                              className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                            >
                              {key}: {Array.isArray(value) ? value.join(', ') : value}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => saveSearch(item)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Save search"
                      >
                        <Heart className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => onSearchFromHistory(item)}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Search again"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => removeFromHistory(item.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Remove from history"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Saved Searches Tab */}
      {activeTab === 'saved' && (
        <div className="space-y-4">
          {filteredSaved.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Bookmark className="w-8 h-8 mx-auto mb-2" />
              <p>No saved searches</p>
              <p className="text-sm mt-1">Save searches from your history to access them quickly</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredSaved.map((item) => (
                <div
                  key={item.savedId}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        {editingSearch === item.savedId ? (
                          <input
                            type="text"
                            value={newSearchName}
                            onChange={(e) => setNewSearchName(e.target.value)}
                            onBlur={() => updateSavedSearchName(item.savedId, newSearchName)}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                updateSavedSearchName(item.savedId, newSearchName);
                              }
                            }}
                            className="text-sm font-medium text-gray-900 border-none p-0 focus:ring-0"
                            autoFocus
                          />
                        ) : (
                          <span className="text-sm font-medium text-gray-900">
                            {item.name}
                          </span>
                        )}
                        <span className="text-xs text-gray-500 capitalize">
                          {item.type}
                        </span>
                      </div>
                      
                      {item.query && (
                        <p className="text-sm text-gray-600 mb-2">"{item.query}"</p>
                      )}
                      
                      {item.imageUrl && (
                        <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden mb-2">
                          <img 
                            src={item.imageUrl} 
                            alt="Search" 
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>Saved {formatTimestamp(item.savedAt)}</span>
                        </span>
                        {item.resultsCount > 0 && (
                          <span className="flex items-center space-x-1">
                            <TrendingUp className="w-3 h-3" />
                            <span>{item.resultsCount} results</span>
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => {
                          setEditingSearch(item.savedId);
                          setNewSearchName(item.name);
                        }}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Edit name"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => onLoadSavedSearch(item)}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Load search"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => removeSavedSearch(item.savedId)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Remove saved search"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchHistory;
