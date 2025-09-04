import React, { useState, useEffect } from 'react';
import ProductGrid from './ProductGrid';

// Mock data for demonstration
const generateMockProducts = (count = 24) => {
  const categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty'];
  const brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony', 'LG', 'Canon', 'Nikon'];
  
  return Array.from({ length: count }, (_, index) => ({
    id: `product-${index + 1}`,
    name: `Amazing Product ${index + 1}`,
    description: `This is a wonderful product that offers great value and excellent quality. Perfect for everyday use and special occasions.`,
    price: Math.floor(Math.random() * 500) + 20,
    original_price: Math.floor(Math.random() * 100) + 500,
    category: categories[Math.floor(Math.random() * categories.length)],
    brand: brands[Math.floor(Math.random() * brands.length)],
    rating: Math.round((Math.random() * 2 + 3) * 10) / 10, // 3.0 to 5.0
    review_count: Math.floor(Math.random() * 1000) + 10,
    image_url: `https://picsum.photos/400/400?random=${index + 1}`,
    stock_quantity: Math.floor(Math.random() * 100),
    is_featured: Math.random() > 0.8,
    is_new: Math.random() > 0.7,
    view_count: Math.floor(Math.random() * 10000),
    created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
  }));
};

const generateMockSimilarityScores = (count) => {
  return Array.from({ length: count }, () => Math.random() * 0.4 + 0.6); // 0.6 to 1.0
};

const ProductGridDemo = () => {
  const [products, setProducts] = useState([]);
  const [similarity_scores, setSimilarityScores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [sortBy, setSortBy] = useState('relevance');
  const [viewMode, setViewMode] = useState('grid');
  
  const ITEMS_PER_PAGE = 20;
  const TOTAL_ITEMS = 100;

  // Initialize with first batch of products
  useEffect(() => {
    const initialProducts = generateMockProducts(ITEMS_PER_PAGE);
    const initialScores = generateMockSimilarityScores(ITEMS_PER_PAGE);
    
    setProducts(initialProducts);
    setSimilarityScores(initialScores);
  }, []);

  // Mock search parameters for demonstration
  const mockSearchParams = {
    mode: 'hybrid',
    query: 'wireless headphones',
    filters: {
      categories: ['Electronics'],
      brands: ['Sony', 'Apple'],
      priceRange: { label: '$100 - $250', min: 100, max: 250 },
      inStockOnly: true,
      minRating: 4
    }
  };

  // Mock explanations for why products match
  const mockExplanations = {
    'product-1': 'High visual similarity • Title matches search • Highly rated product',
    'product-2': 'Good visual match • Description matches • Selected brand',
    'product-3': 'Visual similarity to search criteria • Matches selected category',
    'product-4': 'Title contains search terms • Highly rated product • In selected price range',
    'product-5': 'Description matches • Matches selected brand • Popular product'
  };

  // Handle load more (simulates infinite scroll)
  const handleLoadMore = async () => {
    setLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const remainingItems = TOTAL_ITEMS - products.length;
    const itemsToLoad = Math.min(ITEMS_PER_PAGE, remainingItems);
    
    if (itemsToLoad > 0) {
      const newProducts = generateMockProducts(itemsToLoad);
      const newScores = generateMockSimilarityScores(itemsToLoad);
      
      setProducts(prev => [...prev, ...newProducts]);
      setSimilarityScores(prev => [...prev, ...newScores]);
      setCurrentPage(prev => prev + 1);
      
      // Update explanations for new products
      newProducts.forEach((product, index) => {
        const explanationOptions = [
          'Visual similarity to search criteria',
          'Title contains search terms',
          'Description matches query',
          'Highly rated product',
          'Popular in category',
          'Matches selected filters'
        ];
        const randomExplanations = explanationOptions
          .sort(() => 0.5 - Math.random())
          .slice(0, Math.floor(Math.random() * 3) + 1);
        
        mockExplanations[product.id] = randomExplanations.join(' • ');
      });
    }
    
    setHasMore(products.length + itemsToLoad < TOTAL_ITEMS);
    setLoading(false);
  };

  // Handle sort change
  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    // In a real app, this would trigger a new API call
    console.log('Sort changed to:', newSortBy);
  };

  // Handle view mode change
  const handleViewModeChange = (newViewMode) => {
    setViewMode(newViewMode);
    console.log('View mode changed to:', newViewMode);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Demo Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🛍️ Enhanced Product Grid Demo
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Showcase of all advanced features including infinite scroll, sort options, 
            view modes, hover effects, and "why this matches" explanations.
          </p>
          
          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">🔄 Infinite Scroll</h3>
              <p className="text-sm text-gray-600">Automatically loads more products as you scroll</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">🎯 Smart Explanations</h3>
              <p className="text-sm text-gray-600">Shows why each product matches your search</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">⚡ Quick Actions</h3>
              <p className="text-sm text-gray-600">Save, share, and view details with hover effects</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2">📱 Responsive Design</h3>
              <p className="text-sm text-gray-600">Grid and list views with smooth animations</p>
            </div>
          </div>

          {/* Mock Search Context */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2">📝 Demo Search Context</h3>
            <div className="text-sm text-blue-800 space-y-1">
              <p><strong>Query:</strong> "{mockSearchParams.query}"</p>
              <p><strong>Mode:</strong> {mockSearchParams.mode}</p>
              <p><strong>Filters:</strong> Electronics, Sony & Apple brands, $100-$250, 4+ stars, In stock</p>
            </div>
          </div>
        </div>

        {/* Enhanced Product Grid */}
        <ProductGrid
          products={products}
          similarity_scores={similarity_scores}
          loading={loading}
          error={null}
          searchParams={mockSearchParams}
          onLoadMore={handleLoadMore}
          hasMore={hasMore}
          totalResults={TOTAL_ITEMS}
          currentPage={currentPage}
          onSortChange={handleSortChange}
          onViewModeChange={handleViewModeChange}
          explanations={mockExplanations}
        />

        {/* Demo Footer */}
        <div className="mt-12 bg-gray-100 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">✨ Features Demonstrated</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
            <ul className="space-y-2">
              <li>✅ Responsive grid layout (1-4 columns)</li>
              <li>✅ List view mode with detailed layout</li>
              <li>✅ Infinite scroll with loading states</li>
              <li>✅ Sort by relevance, price, rating, etc.</li>
              <li>✅ Similarity score badges</li>
              <li>✅ Product rating displays</li>
            </ul>
            <ul className="space-y-2">
              <li>✅ Quick actions (save, share, view)</li>
              <li>✅ Hover effects and animations</li>
              <li>✅ "Why this matches" explanations</li>
              <li>✅ Stock status indicators</li>
              <li>✅ Featured and new product badges</li>
              <li>✅ Smooth loading and error states</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductGridDemo;
