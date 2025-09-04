import React, { useState, useCallback } from 'react';
import { 
  Image, 
  Type, 
  Sliders, 
  Info,
  Eye,
  Sparkles
} from 'lucide-react';

const VisualSimilaritySlider = ({ 
  imageWeight = 0.7,
  textWeight = 0.3,
  onChange = () => {},
  disabled = false,
  showTooltip = true
}) => {
  const [localImageWeight, setLocalImageWeight] = useState(imageWeight);
  const [showInfo, setShowInfo] = useState(false);

  // Calculate text weight based on image weight
  const localTextWeight = 1 - localImageWeight;

  const handleSliderChange = useCallback((e) => {
    const newImageWeight = parseFloat(e.target.value);
    const newTextWeight = 1 - newImageWeight;
    
    setLocalImageWeight(newImageWeight);
    
    onChange({
      imageWeight: newImageWeight,
      textWeight: newTextWeight
    });
  }, [onChange]);

  const getWeightLabel = (weight) => {
    if (weight >= 0.8) return 'Very High';
    if (weight >= 0.6) return 'High';
    if (weight >= 0.4) return 'Medium';
    if (weight >= 0.2) return 'Low';
    return 'Very Low';
  };

  const getSliderColor = () => {
    if (localImageWeight >= 0.7) return 'bg-blue-500';
    if (localImageWeight >= 0.5) return 'bg-purple-500';
    return 'bg-green-500';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sliders className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Search Balance</h3>
          {showTooltip && (
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Info className="w-4 h-4" />
            </button>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span className="text-sm text-gray-600">AI Powered</span>
        </div>
      </div>

      {/* Info Panel */}
      {showInfo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">How Search Balance Works:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Higher image weight: Prioritizes visual similarity</li>
                <li>Higher text weight: Focuses on keywords and descriptions</li>
                <li>Balanced settings work best for most searches</li>
                <li>Adjust based on whether you care more about looks or features</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Weight Display */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Image className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Visual Match</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(localImageWeight * 100)}%
          </div>
          <div className="text-xs text-gray-500">
            {getWeightLabel(localImageWeight)}
          </div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Type className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Text Match</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {Math.round(localTextWeight * 100)}%
          </div>
          <div className="text-xs text-gray-500">
            {getWeightLabel(localTextWeight)}
          </div>
        </div>
      </div>

      {/* Slider */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span className="flex items-center space-x-1">
            <Image className="w-3 h-3" />
            <span>Visual</span>
          </span>
          <span className="flex items-center space-x-1">
            <Type className="w-3 h-3" />
            <span>Text</span>
          </span>
        </div>
        
        <div className="relative">
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={localImageWeight}
            onChange={handleSliderChange}
            disabled={disabled}
            className={`w-full h-2 rounded-lg appearance-none cursor-pointer slider ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            style={{
              background: `linear-gradient(to right, 
                #10b981 0%, 
                #8b5cf6 50%, 
                #3b82f6 100%)`
            }}
          />
          
          {/* Slider Thumb Indicator */}
          <div 
            className={`absolute w-4 h-4 ${getSliderColor()} rounded-full shadow-lg transform -translate-y-1/2 transition-all duration-200 ${
              disabled ? 'opacity-50' : 'hover:scale-110'
            }`}
            style={{
              left: `calc(${localImageWeight * 100}% - 8px)`,
              top: '50%'
            }}
          />
        </div>
        
        {/* Scale Labels */}
        <div className="flex justify-between text-xs text-gray-500">
          <span>Text Focus</span>
          <span>Balanced</span>
          <span>Visual Focus</span>
        </div>
      </div>

      {/* Quick Presets */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700">Quick Presets:</p>
        <div className="flex space-x-2">
          <button
            onClick={() => handleSliderChange({ target: { value: '0.3' } })}
            disabled={disabled}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              Math.abs(localImageWeight - 0.3) < 0.1
                ? 'bg-green-100 border-green-300 text-green-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            Text Heavy
          </button>
          <button
            onClick={() => handleSliderChange({ target: { value: '0.5' } })}
            disabled={disabled}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              Math.abs(localImageWeight - 0.5) < 0.1
                ? 'bg-purple-100 border-purple-300 text-purple-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            Balanced
          </button>
          <button
            onClick={() => handleSliderChange({ target: { value: '0.7' } })}
            disabled={disabled}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              Math.abs(localImageWeight - 0.7) < 0.1
                ? 'bg-blue-100 border-blue-300 text-blue-700'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            Visual Heavy
          </button>
        </div>
      </div>

      {/* Current Mode Description */}
      <div className="bg-gray-50 rounded-lg p-3">
        <div className="flex items-center space-x-2 mb-1">
          <Eye className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Current Mode:</span>
        </div>
        <p className="text-xs text-gray-600">
          {localImageWeight >= 0.7 
            ? "Prioritizing visual similarity - great for finding items that look similar to your reference image."
            : localImageWeight >= 0.3
            ? "Balanced search - considering both visual appearance and text descriptions equally."
            : "Text-focused search - emphasizing keywords, descriptions, and product features over visual similarity."
          }
        </p>
      </div>
    </div>
  );
};

export default VisualSimilaritySlider;
