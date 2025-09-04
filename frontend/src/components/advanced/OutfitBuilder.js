import React, { useState, useCallback } from 'react';
import { 
  Plus, 
  X, 
  ShoppingBag, 
  Shirt, 
  Watch,
  Eye,
  Sparkles,
  Shuffle,
  Heart,
  Share2,
  ArrowRight,
  Info,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

const OutfitBuilder = ({ 
  onOutfitSearch = () => {},
  onSaveOutfit = () => {},
  onShareOutfit = () => {},
  loading = false,
  disabled = false
}) => {
  const [outfitItems, setOutfitItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [outfitName, setOutfitName] = useState('');
  const [outfitOccasion, setOutfitOccasion] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [draggedItem, setDraggedItem] = useState(null);

  // Outfit categories
  const categories = [
    { id: 'tops', name: 'Tops', icon: Shirt, color: 'blue' },
    { id: 'bottoms', name: 'Bottoms', icon: ShoppingBag, color: 'green' },
    { id: 'shoes', name: 'Shoes', icon: '👟', color: 'purple' },
    { id: 'accessories', name: 'Accessories', icon: Watch, color: 'orange' },
    { id: 'outerwear', name: 'Outerwear', icon: '🧥', color: 'gray' },
    { id: 'bags', name: 'Bags', icon: '👜', color: 'pink' }
  ];

  // Occasions
  const occasions = [
    'Casual', 'Work/Professional', 'Date Night', 'Party/Event', 
    'Workout/Athletic', 'Beach/Vacation', 'Formal/Black Tie', 'Weekend'
  ];

  // Add item to outfit
  const addItemToOutfit = useCallback((item, category) => {
    const newItem = {
      id: Date.now() + Math.random(),
      category,
      item,
      position: { x: 0, y: 0 }
    };
    
    setOutfitItems(prev => [...prev, newItem]);
  }, []);

  // Remove item from outfit
  const removeItemFromOutfit = useCallback((itemId) => {
    setOutfitItems(prev => prev.filter(item => item.id !== itemId));
  }, []);

  // Handle drag start
  const handleDragStart = (e, item) => {
    setDraggedItem(item);
    e.dataTransfer.effectAllowed = 'move';
  };

  // Handle drag over
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  // Handle drop
  const handleDrop = (e) => {
    e.preventDefault();
    if (!draggedItem) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setOutfitItems(prev => 
      prev.map(item => 
        item.id === draggedItem.id 
          ? { ...item, position: { x, y } }
          : item
      )
    );
    setDraggedItem(null);
  };

  // Generate outfit combinations
  const generateOutfitCombinations = () => {
    if (outfitItems.length < 2) return;
    
    const searchParams = {
      items: outfitItems.map(item => ({
        category: item.category,
        description: item.item.name || item.item.description,
        style: item.item.style,
        color: item.item.color
      })),
      occasion: outfitOccasion,
      style: 'coordinated'
    };
    
    onOutfitSearch(searchParams);
  };

  // Save outfit
  const saveOutfit = () => {
    if (!outfitName.trim()) return;
    
    const outfit = {
      name: outfitName,
      occasion: outfitOccasion,
      items: outfitItems,
      createdAt: new Date().toISOString()
    };
    
    onSaveOutfit(outfit);
  };

  // Share outfit
  const shareOutfit = () => {
    const outfit = {
      name: outfitName || 'My Outfit',
      items: outfitItems,
      occasion: outfitOccasion
    };
    
    onShareOutfit(outfit);
  };

  // Get category color
  const getCategoryColor = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.color || 'gray';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ShoppingBag className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Outfit Builder</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span className="text-sm text-gray-600">AI Stylist</span>
        </div>
      </div>

      {/* Description */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Create complete outfits</p>
            <p className="text-xs">Add items from different categories to build an outfit, then find similar coordinated pieces.</p>
          </div>
        </div>
      </div>

      {/* Outfit Setup */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Outfit Name
            </label>
            <input
              type="text"
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              placeholder="e.g., Summer Date Night"
              disabled={disabled}
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                disabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Occasion
            </label>
            <select
              value={outfitOccasion}
              onChange={(e) => setOutfitOccasion(e.target.value)}
              disabled={disabled}
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                disabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <option value="">Select occasion</option>
              {occasions.map((occasion) => (
                <option key={occasion} value={occasion}>
                  {occasion}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Category Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">Add Items by Category:</label>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
          {categories.map((category) => {
            const Icon = category.icon;
            const itemCount = outfitItems.filter(item => item.category === category.id).length;
            
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                disabled={disabled}
                className={`relative flex flex-col items-center p-3 rounded-lg border transition-colors ${
                  selectedCategory === category.id
                    ? `bg-${category.color}-100 border-${category.color}-300 text-${category.color}-700`
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                {typeof Icon === 'string' ? (
                  <span className="text-lg mb-1">{Icon}</span>
                ) : (
                  <Icon className="w-5 h-5 mb-1" />
                )}
                <span className="text-xs font-medium">{category.name}</span>
                
                {itemCount > 0 && (
                  <div className={`absolute -top-1 -right-1 w-5 h-5 bg-${category.color}-500 text-white text-xs rounded-full flex items-center justify-center`}>
                    {itemCount}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Outfit Canvas */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">Current Outfit:</label>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              disabled={disabled || outfitItems.length === 0}
              className={`p-1 text-gray-400 hover:text-gray-600 transition-colors ${
                disabled || outfitItems.length === 0 ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <Shuffle className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div
          className="relative min-h-64 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-4"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {outfitItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-gray-500">
              <Plus className="w-8 h-8 mb-2" />
              <p className="text-sm">Add items to build your outfit</p>
              <p className="text-xs">Select categories above to add items</p>
            </div>
          ) : (
            <div className="space-y-3">
              {outfitItems.map((item) => (
                <div
                  key={item.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, item)}
                  className={`relative flex items-center space-x-3 p-3 bg-white border-2 border-${getCategoryColor(item.category)}-200 rounded-lg cursor-move hover:shadow-md transition-all`}
                >
                  <div className={`w-12 h-12 bg-${getCategoryColor(item.category)}-100 rounded-lg flex items-center justify-center`}>
                    {categories.find(c => c.id === item.category)?.icon === 'string' ? (
                      <span className="text-lg">
                        {categories.find(c => c.id === item.category)?.icon}
                      </span>
                    ) : (
                      <Shirt className="w-6 h-6 text-gray-600" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.item.name || `${item.category} item`}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">
                      {item.category}
                    </p>
                  </div>
                  
                  <button
                    onClick={() => removeItemFromOutfit(item.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Add Items */}
      {selectedCategory && (
        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-700">
            Quick Add {categories.find(c => c.id === selectedCategory)?.name}:
          </label>
          <div className="grid grid-cols-2 gap-3">
            {/* Sample items for demonstration */}
            {[
              { name: 'Basic T-Shirt', color: 'white', style: 'casual' },
              { name: 'Button-Down Shirt', color: 'blue', style: 'formal' },
              { name: 'Blazer', color: 'navy', style: 'professional' },
              { name: 'Sweater', color: 'gray', style: 'cozy' }
            ].map((sampleItem, index) => (
              <button
                key={index}
                onClick={() => addItemToOutfit(sampleItem, selectedCategory)}
                disabled={disabled}
                className={`flex items-center space-x-2 p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors ${
                  disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                }`}
              >
                <Plus className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{sampleItem.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Outfit Actions */}
      {outfitItems.length > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <button
              onClick={saveOutfit}
              disabled={disabled || !outfitName.trim()}
              className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${
                disabled || !outfitName.trim() ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <Heart className="w-4 h-4" />
              <span className="text-sm">Save</span>
            </button>
            
            <button
              onClick={shareOutfit}
              disabled={disabled}
              className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${
                disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <Share2 className="w-4 h-4" />
              <span className="text-sm">Share</span>
            </button>
          </div>

          <button
            onClick={generateOutfitCombinations}
            disabled={disabled || loading || outfitItems.length < 2}
            className={`flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium transition-colors ${
              disabled || loading || outfitItems.length < 2
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-blue-700 cursor-pointer'
            }`}
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Finding...</span>
              </>
            ) : (
              <>
                <span>Find Complete Outfits</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      )}

      {/* Suggestions */}
      {showSuggestions && outfitItems.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">AI Styling Suggestions:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Add a {categories.find(c => !outfitItems.some(item => item.category === c.id))?.name.toLowerCase()} to complete your look</li>
                <li>Consider accessories to elevate the outfit</li>
                <li>Match colors and styles for better coordination</li>
                {outfitOccasion && <li>Perfect for {outfitOccasion.toLowerCase()} occasions</li>}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Status Messages */}
      {outfitItems.length < 2 && outfitItems.length > 0 && (
        <div className="flex items-center space-x-2 text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-lg p-3">
          <AlertTriangle className="w-4 h-4" />
          <span>Add at least 2 items to generate outfit combinations</span>
        </div>
      )}
    </div>
  );
};

export default OutfitBuilder;
