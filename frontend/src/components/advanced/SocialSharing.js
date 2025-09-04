import React, { useState } from 'react';
import { 
  Share2, 
  Copy, 
  Facebook, 
  Twitter, 
  MessageCircle,
  Mail,
  Link,
  Download,
  QrCode,
  CheckCircle,
  ExternalLink,
  Users,
  Heart,
  ShoppingCart,
  Sparkles
} from 'lucide-react';

const SocialSharing = ({ 
  searchResults = [],
  searchQuery = '',
  searchType = 'text',
  searchImage = null,
  onCreateWishlist = () => {},
  onCreateCollection = () => {},
  disabled = false
}) => {
  const [copied, setCopied] = useState(false);
  const [shareMode, setShareMode] = useState('results'); // 'results', 'wishlist', 'collection'
  const [shareTitle, setShareTitle] = useState('');
  const [shareDescription, setShareDescription] = useState('');
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [showQRCode, setShowQRCode] = useState(false);

  // Generate share URL
  const generateShareURL = () => {
    const baseUrl = window.location.origin;
    const params = new URLSearchParams();
    
    if (searchQuery) params.set('q', searchQuery);
    if (searchType) params.set('type', searchType);
    if (selectedItems.size > 0) {
      params.set('items', Array.from(selectedItems).join(','));
    }
    
    return `${baseUrl}/search?${params.toString()}`;
  };

  // Copy to clipboard
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  // Share via native API
  const shareNative = async () => {
    if (!navigator.share) return false;
    
    try {
      await navigator.share({
        title: shareTitle || `Search Results: ${searchQuery}`,
        text: shareDescription || `Check out these products I found!`,
        url: generateShareURL()
      });
      return true;
    } catch (error) {
      console.error('Native sharing failed:', error);
      return false;
    }
  };

  // Share to social platforms
  const shareToSocial = (platform) => {
    const url = generateShareURL();
    const title = encodeURIComponent(shareTitle || `Check out these products: ${searchQuery}`);
    const description = encodeURIComponent(shareDescription || 'Amazing products I found!');
    
    let shareUrl = '';
    
    switch (platform) {
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
        break;
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${title}&url=${encodeURIComponent(url)}`;
        break;
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${title}%20${encodeURIComponent(url)}`;
        break;
      case 'telegram':
        shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${title}`;
        break;
      case 'email':
        shareUrl = `mailto:?subject=${title}&body=${description}%0A%0A${encodeURIComponent(url)}`;
        break;
      default:
        return;
    }
    
    window.open(shareUrl, '_blank', 'width=600,height=400');
  };

  // Toggle item selection
  const toggleItemSelection = (itemId) => {
    const newSelection = new Set(selectedItems);
    if (newSelection.has(itemId)) {
      newSelection.delete(itemId);
    } else {
      newSelection.add(itemId);
    }
    setSelectedItems(newSelection);
  };

  // Select all items
  const selectAllItems = () => {
    setSelectedItems(new Set(searchResults.map(item => item.id)));
  };

  // Clear selection
  const clearSelection = () => {
    setSelectedItems(new Set());
  };

  // Create wishlist from selection
  const createWishlist = () => {
    const selectedProducts = searchResults.filter(item => selectedItems.has(item.id));
    const wishlist = {
      title: shareTitle || `My Wishlist - ${searchQuery}`,
      description: shareDescription,
      items: selectedProducts,
      createdAt: new Date().toISOString(),
      isPublic: true
    };
    onCreateWishlist(wishlist);
  };

  // Create collection from selection
  const createCollection = () => {
    const selectedProducts = searchResults.filter(item => selectedItems.has(item.id));
    const collection = {
      title: shareTitle || `My Collection - ${searchQuery}`,
      description: shareDescription,
      items: selectedProducts,
      createdAt: new Date().toISOString(),
      isPublic: true
    };
    onCreateCollection(collection);
  };

  // Generate QR code data
  const generateQRCodeData = () => {
    return generateShareURL();
  };

  const shareUrl = generateShareURL();

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Share2 className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Share Results</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <Users className="w-4 h-4 text-green-500" />
          <span className="text-sm text-gray-600">Social Sharing</span>
        </div>
      </div>

      {/* Share Mode Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700">What would you like to share?</label>
        <div className="flex space-x-2">
          {[
            { mode: 'results', label: 'Search Results', icon: Share2 },
            { mode: 'wishlist', label: 'Create Wishlist', icon: Heart },
            { mode: 'collection', label: 'Create Collection', icon: ShoppingCart }
          ].map(({ mode, label, icon: Icon }) => (
            <button
              key={mode}
              onClick={() => setShareMode(mode)}
              disabled={disabled}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                shareMode === mode
                  ? 'bg-blue-100 border-blue-300 text-blue-700'
                  : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Item Selection for Wishlist/Collection */}
      {(shareMode === 'wishlist' || shareMode === 'collection') && searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">
              Select items ({selectedItems.size} of {searchResults.length} selected):
            </label>
            <div className="flex space-x-2">
              <button
                onClick={selectAllItems}
                disabled={disabled}
                className={`text-sm text-blue-600 hover:text-blue-800 transition-colors ${
                  disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                }`}
              >
                Select All
              </button>
              <button
                onClick={clearSelection}
                disabled={disabled || selectedItems.size === 0}
                className={`text-sm text-gray-600 hover:text-gray-800 transition-colors ${
                  disabled || selectedItems.size === 0 ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                }`}
              >
                Clear
              </button>
            </div>
          </div>
          
          <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
            <div className="grid grid-cols-1 gap-2 p-3">
              {searchResults.map((item) => (
                <div
                  key={item.id}
                  className={`flex items-center space-x-3 p-2 rounded-lg border transition-colors cursor-pointer ${
                    selectedItems.has(item.id)
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                  onClick={() => toggleItemSelection(item.id)}
                >
                  <input
                    type="checkbox"
                    checked={selectedItems.has(item.id)}
                    onChange={() => toggleItemSelection(item.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="w-12 h-12 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                    <img 
                      src={item.image_url || '/api/placeholder/48/48'} 
                      alt={item.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
                    <p className="text-sm text-gray-600">${item.price}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Share Content */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {shareMode === 'results' ? 'Share Title' : 
             shareMode === 'wishlist' ? 'Wishlist Name' : 'Collection Name'}
          </label>
          <input
            type="text"
            value={shareTitle}
            onChange={(e) => setShareTitle(e.target.value)}
            placeholder={
              shareMode === 'results' ? `Search Results: ${searchQuery}` :
              shareMode === 'wishlist' ? 'My Wishlist' : 'My Collection'
            }
            disabled={disabled}
            className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            value={shareDescription}
            onChange={(e) => setShareDescription(e.target.value)}
            placeholder="Add a description to share with your friends..."
            rows={3}
            disabled={disabled}
            className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          />
        </div>
      </div>

      {/* Share URL Preview */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Share Link:</label>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={shareUrl}
            readOnly
            className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm"
          />
          <button
            onClick={() => copyToClipboard(shareUrl)}
            disabled={disabled}
            className={`flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            {copied ? (
              <>
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span className="text-sm">Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Social Platform Buttons */}
      <div className="space-y-4">
        <label className="text-sm font-medium text-gray-700">Share to:</label>
        
        {/* Native Share (if available) */}
        {navigator.share && (
          <button
            onClick={shareNative}
            disabled={disabled}
            className={`w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Share (Native)</span>
          </button>
        )}
        
        {/* Social Platform Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[
            { platform: 'facebook', label: 'Facebook', icon: Facebook, color: 'bg-blue-600 hover:bg-blue-700' },
            { platform: 'twitter', label: 'Twitter', icon: Twitter, color: 'bg-sky-500 hover:bg-sky-600' },
            { platform: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, color: 'bg-green-600 hover:bg-green-700' },
            { platform: 'telegram', label: 'Telegram', icon: ExternalLink, color: 'bg-blue-500 hover:bg-blue-600' },
            { platform: 'email', label: 'Email', icon: Mail, color: 'bg-gray-600 hover:bg-gray-700' },
          ].map(({ platform, label, icon: Icon, color }) => (
            <button
              key={platform}
              onClick={() => shareToSocial(platform)}
              disabled={disabled}
              className={`flex items-center justify-center space-x-2 px-4 py-3 text-white rounded-lg transition-colors ${color} ${
                disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Additional Actions */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
        {shareMode === 'wishlist' && selectedItems.size > 0 && (
          <button
            onClick={createWishlist}
            disabled={disabled}
            className={`flex items-center space-x-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            <Heart className="w-4 h-4" />
            <span>Create Wishlist</span>
          </button>
        )}
        
        {shareMode === 'collection' && selectedItems.size > 0 && (
          <button
            onClick={createCollection}
            disabled={disabled}
            className={`flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            }`}
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Create Collection</span>
          </button>
        )}
        
        <button
          onClick={() => setShowQRCode(!showQRCode)}
          disabled={disabled}
          className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${
            disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          }`}
        >
          <QrCode className="w-4 h-4" />
          <span>QR Code</span>
        </button>
        
        <button
          onClick={() => {
            const element = document.createElement('a');
            element.href = shareUrl;
            element.download = 'search-results.txt';
            element.click();
          }}
          disabled={disabled}
          className={`flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${
            disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          }`}
        >
          <Download className="w-4 h-4" />
          <span>Download</span>
        </button>
      </div>

      {/* QR Code Display */}
      {showQRCode && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <div className="w-32 h-32 bg-white border border-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center">
            {/* QR Code would be generated here with a library like qrcode */}
            <div className="text-gray-400">
              <QrCode className="w-16 h-16" />
            </div>
          </div>
          <p className="text-sm text-gray-600">
            Scan this QR code to share the search results
          </p>
          <p className="text-xs text-gray-500 mt-1">
            QR Code generation requires additional library
          </p>
        </div>
      )}

      {/* Status Messages */}
      {shareMode !== 'results' && selectedItems.size === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <Heart className="w-4 h-4 text-amber-600" />
            <span className="text-sm text-amber-800">
              Select items to create a {shareMode}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialSharing;
