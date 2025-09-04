import React, { useState } from 'react';
import { 
  Settings, 
  Wand2, 
  ShoppingBag, 
  DollarSign, 
  Clock, 
  Share2,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Zap
} from 'lucide-react';
import {
  VisualSimilaritySlider,
  StyleTransferInterface,
  OutfitBuilder,
  PriceComparison,
  SearchHistory,
  SocialSharing
} from './advanced';

const AdvancedSearchInterface = ({ 
  searchResults = [],
  currentProduct = null,
  onAdvancedSearch = () => {},
  onStyleTransfer = () => {},
  onOutfitSearch = () => {},
  onPriceComparison = () => {},
  loading = false
}) => {
  const [activeSection, setActiveSection] = useState('similarity');
  const [expandedSections, setExpandedSections] = useState(new Set(['similarity']));

  // Section configuration
  const sections = [
    {
      id: 'similarity',
      title: 'Search Balance',
      icon: Settings,
      description: 'Adjust image vs text search weight',
      component: VisualSimilaritySlider,
      color: 'blue'
    },
    {
      id: 'style-transfer',
      title: 'Style Transfer',
      icon: Wand2,
      description: 'Find similar items with different styles',
      component: StyleTransferInterface,
      color: 'purple'
    },
    {
      id: 'outfit-builder',
      title: 'Outfit Builder',
      icon: ShoppingBag,
      description: 'Create complete outfit combinations',
      component: OutfitBuilder,
      color: 'green'
    },
    {
      id: 'price-comparison',
      title: 'Price Comparison',
      icon: DollarSign,
      description: 'Compare prices and find alternatives',
      component: PriceComparison,
      color: 'orange'
    },
    {
      id: 'search-history',
      title: 'Search History',
      icon: Clock,
      description: 'View and manage search history',
      component: SearchHistory,
      color: 'indigo'
    },
    {
      id: 'social-sharing',
      title: 'Social Sharing',
      icon: Share2,
      description: 'Share search results and collections',
      component: SocialSharing,
      color: 'pink'
    }
  ];

  // Toggle section expansion
  const toggleSection = (sectionId) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
    setActiveSection(sectionId);
  };

  // Get component props for each section
  const getComponentProps = (sectionId) => {
    const baseProps = { loading };
    
    switch (sectionId) {
      case 'similarity':
        return {
          ...baseProps,
          onChange: (weights) => onAdvancedSearch({ searchWeights: weights })
        };
      
      case 'style-transfer':
        return {
          ...baseProps,
          originalImage: currentProduct?.image_url,
          onStyleTransfer
        };
      
      case 'outfit-builder':
        return {
          ...baseProps,
          onOutfitSearch
        };
      
      case 'price-comparison':
        return {
          ...baseProps,
          product: currentProduct,
          alternatives: searchResults.filter(item => item.id !== currentProduct?.id),
          onAddToCart: (product) => console.log('Add to cart:', product),
          onSaveProduct: (productId) => console.log('Save product:', productId)
        };
      
      case 'search-history':
        return {
          ...baseProps,
          onSearchFromHistory: (search) => onAdvancedSearch({ fromHistory: search }),
          onSaveSearch: (search) => console.log('Save search:', search),
          onLoadSavedSearch: (search) => onAdvancedSearch({ savedSearch: search })
        };
      
      case 'social-sharing':
        return {
          ...baseProps,
          searchResults,
          searchQuery: 'Current search query',
          onCreateWishlist: (wishlist) => console.log('Create wishlist:', wishlist),
          onCreateCollection: (collection) => console.log('Create collection:', collection)
        };
      
      default:
        return baseProps;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Sparkles className="w-8 h-8" />
          <h2 className="text-2xl font-bold">Advanced Search Features</h2>
        </div>
        <p className="text-blue-100 mb-4">
          Powerful AI-driven tools to enhance your shopping experience
        </p>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{sections.length}</div>
            <div className="text-sm text-blue-200">AI Tools</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{searchResults.length}</div>
            <div className="text-sm text-blue-200">Results</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">
              <Zap className="w-6 h-6 inline" />
            </div>
            <div className="text-sm text-blue-200">AI Powered</div>
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {sections.map((section) => {
            const Icon = section.icon;
            const isActive = activeSection === section.id;
            const isExpanded = expandedSections.has(section.id);
            
            return (
              <button
                key={section.id}
                onClick={() => toggleSection(section.id)}
                className={`flex flex-col items-center p-3 rounded-lg border transition-all ${
                  isActive
                    ? `bg-${section.color}-100 border-${section.color}-300 text-${section.color}-700`
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-6 h-6 mb-2" />
                <span className="text-xs font-medium text-center leading-tight">
                  {section.title}
                </span>
                {isExpanded ? (
                  <ChevronUp className="w-3 h-3 mt-1" />
                ) : (
                  <ChevronDown className="w-3 h-3 mt-1" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Section Content */}
      <div className="space-y-4">
        {sections.map((section) => {
          const Component = section.component;
          const isExpanded = expandedSections.has(section.id);
          
          if (!isExpanded) return null;
          
          return (
            <div key={section.id} className="space-y-2">
              {/* Section Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <section.icon className={`w-5 h-5 text-${section.color}-600`} />
                  <h3 className="text-lg font-semibold text-gray-900">
                    {section.title}
                  </h3>
                </div>
                <p className="text-sm text-gray-600">{section.description}</p>
              </div>
              
              {/* Section Component */}
              <Component {...getComponentProps(section.id)} />
            </div>
          );
        })}
      </div>

      {/* Global Actions */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">
              AI-Powered Search Enhancement
            </span>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setExpandedSections(new Set(sections.map(s => s.id)))}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              Expand All
            </button>
            <button
              onClick={() => setExpandedSections(new Set())}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Collapse All
            </button>
          </div>
        </div>
        
        <div className="mt-3 text-xs text-gray-500">
          Advanced features powered by AI to help you discover products more effectively.
          Use the tools above to refine your search, compare prices, build outfits, and share your findings.
        </div>
      </div>
    </div>
  );
};

export default AdvancedSearchInterface;
