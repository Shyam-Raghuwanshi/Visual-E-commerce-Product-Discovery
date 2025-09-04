import React, { useState, useRef } from 'react';
import { 
  Palette, 
  Wand2, 
  Upload, 
  X,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Eye,
  ArrowRight
} from 'lucide-react';

const StyleTransferInterface = ({ 
  originalImage = null,
  onStyleTransfer = () => {},
  loading = false,
  disabled = false
}) => {
  const [selectedStyle, setSelectedStyle] = useState('');
  const [customColor, setCustomColor] = useState('#3B82F6');
  const [styleMode, setStyleMode] = useState('color'); // 'color', 'pattern', 'material'
  const [customStyleImage, setCustomStyleImage] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  
  const fileInputRef = useRef();

  // Predefined color options
  const colorOptions = [
    { name: 'Blue', value: '#3B82F6', gradient: 'from-blue-400 to-blue-600' },
    { name: 'Red', value: '#EF4444', gradient: 'from-red-400 to-red-600' },
    { name: 'Green', value: '#10B981', gradient: 'from-green-400 to-green-600' },
    { name: 'Purple', value: '#8B5CF6', gradient: 'from-purple-400 to-purple-600' },
    { name: 'Pink', value: '#EC4899', gradient: 'from-pink-400 to-pink-600' },
    { name: 'Yellow', value: '#F59E0B', gradient: 'from-yellow-400 to-yellow-600' },
    { name: 'Black', value: '#1F2937', gradient: 'from-gray-700 to-gray-900' },
    { name: 'White', value: '#F9FAFB', gradient: 'from-gray-100 to-gray-300' }
  ];

  // Pattern options
  const patternOptions = [
    { name: 'Stripes', value: 'stripes', icon: '|||' },
    { name: 'Polka Dots', value: 'polka-dots', icon: '•••' },
    { name: 'Plaid', value: 'plaid', icon: '▦' },
    { name: 'Floral', value: 'floral', icon: '❀' },
    { name: 'Geometric', value: 'geometric', icon: '◆' },
    { name: 'Animal Print', value: 'animal-print', icon: '🐆' },
    { name: 'Abstract', value: 'abstract', icon: '~' },
    { name: 'Solid', value: 'solid', icon: '■' }
  ];

  // Material options
  const materialOptions = [
    { name: 'Cotton', value: 'cotton', description: 'Soft and breathable' },
    { name: 'Silk', value: 'silk', description: 'Smooth and luxurious' },
    { name: 'Denim', value: 'denim', description: 'Durable and casual' },
    { name: 'Leather', value: 'leather', description: 'Premium and stylish' },
    { name: 'Wool', value: 'wool', description: 'Warm and cozy' },
    { name: 'Linen', value: 'linen', description: 'Light and airy' },
    { name: 'Velvet', value: 'velvet', description: 'Rich and elegant' },
    { name: 'Satin', value: 'satin', description: 'Shiny and formal' }
  ];

  // Handle custom style image upload
  const handleStyleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCustomStyleImage(e.target.result);
        setSelectedStyle('custom-image');
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle style transfer
  const handleStyleTransfer = () => {
    const styleParams = {
      mode: styleMode,
      style: selectedStyle,
      color: customColor,
      customImage: customStyleImage,
      query: searchQuery
    };
    
    onStyleTransfer(styleParams);
  };

  // Generate search query based on selections
  const generateSearchQuery = () => {
    if (!originalImage) return '';
    
    let query = 'similar item';
    
    if (styleMode === 'color' && selectedStyle) {
      const colorName = colorOptions.find(c => c.value === selectedStyle)?.name || 'colored';
      query += ` in ${colorName.toLowerCase()}`;
    } else if (styleMode === 'pattern' && selectedStyle) {
      const patternName = patternOptions.find(p => p.value === selectedStyle)?.name || 'patterned';
      query += ` with ${patternName.toLowerCase()} pattern`;
    } else if (styleMode === 'material' && selectedStyle) {
      const materialName = materialOptions.find(m => m.value === selectedStyle)?.name || 'material';
      query += ` in ${materialName.toLowerCase()}`;
    }
    
    return query;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Wand2 className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">Style Transfer</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span className="text-sm text-gray-600">AI Powered</span>
        </div>
      </div>

      {/* Description */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Palette className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-purple-800">
            <p className="font-medium mb-1">Find similar items with different styles</p>
            <p className="text-xs">Upload or search for an item, then specify how you want it styled - different colors, patterns, or materials.</p>
          </div>
        </div>
      </div>

      {/* Original Image Preview */}
      {originalImage && (
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Original Image:</label>
          <div className="relative w-32 h-32 rounded-lg overflow-hidden border-2 border-gray-200">
            <img 
              src={originalImage} 
              alt="Original" 
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      )}

      {/* Style Mode Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">Style Type:</label>
        <div className="flex space-x-2">
          {[
            { mode: 'color', label: 'Color', icon: Palette },
            { mode: 'pattern', label: 'Pattern', icon: Wand2 },
            { mode: 'material', label: 'Material', icon: Sparkles }
          ].map(({ mode, label, icon: Icon }) => (
            <button
              key={mode}
              onClick={() => {
                setStyleMode(mode);
                setSelectedStyle('');
              }}
              disabled={disabled}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                styleMode === mode
                  ? 'bg-purple-100 border-purple-300 text-purple-700'
                  : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Color Selection */}
      {styleMode === 'color' && (
        <div className="space-y-4">
          <label className="text-sm font-medium text-gray-700">Select Color:</label>
          
          {/* Predefined Colors */}
          <div className="grid grid-cols-4 gap-3">
            {colorOptions.map((color) => (
              <button
                key={color.value}
                onClick={() => {
                  setSelectedStyle(color.value);
                  setCustomColor(color.value);
                }}
                disabled={disabled}
                className={`relative h-12 rounded-lg border-2 transition-all ${
                  selectedStyle === color.value
                    ? 'border-gray-800 ring-2 ring-purple-500 ring-offset-2'
                    : 'border-gray-200 hover:border-gray-300'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div 
                  className={`w-full h-full rounded-md bg-gradient-to-br ${color.gradient}`}
                />
                {selectedStyle === color.value && (
                  <CheckCircle className="absolute -top-1 -right-1 w-5 h-5 text-purple-600 bg-white rounded-full" />
                )}
                <span className="absolute bottom-0 left-0 right-0 text-xs text-center text-white bg-black bg-opacity-50 py-1 rounded-b-md">
                  {color.name}
                </span>
              </button>
            ))}
          </div>

          {/* Custom Color Picker */}
          <div className="flex items-center space-x-3">
            <label className="text-sm text-gray-600">Custom color:</label>
            <input
              type="color"
              value={customColor}
              onChange={(e) => {
                setCustomColor(e.target.value);
                setSelectedStyle(e.target.value);
              }}
              disabled={disabled}
              className={`w-12 h-8 rounded border border-gray-300 cursor-pointer ${
                disabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            />
            <span className="text-sm text-gray-500">{customColor}</span>
          </div>
        </div>
      )}

      {/* Pattern Selection */}
      {styleMode === 'pattern' && (
        <div className="space-y-4">
          <label className="text-sm font-medium text-gray-700">Select Pattern:</label>
          <div className="grid grid-cols-2 gap-3">
            {patternOptions.map((pattern) => (
              <button
                key={pattern.value}
                onClick={() => setSelectedStyle(pattern.value)}
                disabled={disabled}
                className={`flex items-center space-x-3 p-3 rounded-lg border transition-colors ${
                  selectedStyle === pattern.value
                    ? 'bg-purple-100 border-purple-300 text-purple-700'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span className="text-lg">{pattern.icon}</span>
                <span className="text-sm font-medium">{pattern.name}</span>
                {selectedStyle === pattern.value && (
                  <CheckCircle className="w-4 h-4 text-purple-600 ml-auto" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Material Selection */}
      {styleMode === 'material' && (
        <div className="space-y-4">
          <label className="text-sm font-medium text-gray-700">Select Material:</label>
          <div className="grid grid-cols-1 gap-2">
            {materialOptions.map((material) => (
              <button
                key={material.value}
                onClick={() => setSelectedStyle(material.value)}
                disabled={disabled}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  selectedStyle === material.value
                    ? 'bg-purple-100 border-purple-300 text-purple-700'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div>
                  <span className="text-sm font-medium">{material.name}</span>
                  <p className="text-xs text-gray-500">{material.description}</p>
                </div>
                {selectedStyle === material.value && (
                  <CheckCircle className="w-4 h-4 text-purple-600" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Custom Style Image Upload */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">Or upload reference style image:</label>
        <div className="flex items-center space-x-3">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleStyleImageUpload}
            disabled={disabled}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span className="text-sm">Upload Style Image</span>
          </button>
          
          {customStyleImage && (
            <div className="relative w-16 h-16 rounded-lg overflow-hidden border-2 border-purple-300">
              <img 
                src={customStyleImage} 
                alt="Style reference" 
                className="w-full h-full object-cover"
              />
              <button
                onClick={() => {
                  setCustomStyleImage(null);
                  setSelectedStyle('');
                }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Generated Search Preview */}
      {selectedStyle && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Eye className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">Search Preview:</span>
          </div>
          <p className="text-sm text-blue-700">
            {generateSearchQuery() || 'Please select a style option above'}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <button
          onClick={() => {
            setSelectedStyle('');
            setCustomStyleImage(null);
            setSearchQuery('');
          }}
          disabled={disabled || loading}
          className={`flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors ${
            disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          }`}
        >
          <RefreshCw className="w-4 h-4" />
          <span>Reset</span>
        </button>

        <button
          onClick={handleStyleTransfer}
          disabled={disabled || loading || !selectedStyle || !originalImage}
          className={`flex items-center space-x-2 px-6 py-2 bg-purple-600 text-white rounded-lg font-medium transition-colors ${
            disabled || loading || !selectedStyle || !originalImage
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-purple-700 cursor-pointer'
          }`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <span>Find Similar Items</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {/* Error/Status Messages */}
      {!originalImage && (
        <div className="flex items-center space-x-2 text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-lg p-3">
          <AlertCircle className="w-4 h-4" />
          <span>Please upload an image first to use style transfer</span>
        </div>
      )}
    </div>
  );
};

export default StyleTransferInterface;
