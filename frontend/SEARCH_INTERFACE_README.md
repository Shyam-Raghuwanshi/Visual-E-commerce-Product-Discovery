# Main Search Interface Documentation

## Overview

The `MainSearchInterface` is a comprehensive React component that provides a modern, feature-rich search experience for the Visual E-commerce Product Discovery system. It supports multiple search modes, advanced filtering, and provides an intuitive user interface.

## Features

### Search Modes
- **Text Search**: Traditional keyword-based search
- **Image Search**: Upload images to find similar products
- **Hybrid Search**: Combine text and image for enhanced accuracy

### Advanced Filtering
- **Categories**: Filter by product categories
- **Brands**: Filter by specific brands
- **Price Ranges**: Predefined ranges or custom min/max
- **Stock Status**: Show only in-stock items
- **Ratings**: Minimum rating filter
- **Sorting**: Multiple sort options

### User Experience
- **Drag & Drop**: Image upload with visual feedback
- **Autocomplete**: Smart text suggestions
- **Mobile Responsive**: Optimized for all device sizes
- **Loading States**: Clear feedback during operations
- **Error Handling**: User-friendly error messages

## Usage

### Basic Implementation

```jsx
import React from 'react';
import MainSearchInterface from '../components/MainSearchInterface';
import useSearch from '../hooks/useSearch';

const SearchPage = () => {
  const { performSearch, isLoading } = useSearch();

  const handleSearch = async (searchParams) => {
    try {
      const results = await performSearch(searchParams);
      // Handle results
      console.log('Search results:', results);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <MainSearchInterface 
        onSearch={handleSearch}
        isLoading={isLoading}
      />
    </div>
  );
};
```

### With Initial State

```jsx
<MainSearchInterface 
  onSearch={handleSearch}
  isLoading={isLoading}
  initialQuery="laptop"
  initialFilters={{
    categories: ['electronics'],
    brands: ['Apple', 'Dell'],
    priceRange: { label: '$500 - $1000', min: 500, max: 1000 },
    inStockOnly: true,
    minRating: 4
  }}
/>
```

## Search Parameters

The `onSearch` callback receives a comprehensive `searchParams` object:

```typescript
interface SearchParams {
  mode: 'text' | 'image' | 'hybrid';
  query?: string;
  image?: File;
  filters: {
    categories: string[];
    brands: string[];
    priceRange?: { label: string; min: number; max: number | null };
    minPrice?: number;
    maxPrice?: number;
    sortBy: string;
    inStockOnly: boolean;
    minRating: number;
  };
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onSearch` | `(params: SearchParams) => void` | Required | Callback when search is performed |
| `isLoading` | `boolean` | `false` | Show loading state |
| `initialQuery` | `string` | `''` | Pre-fill text search |
| `initialFilters` | `object` | `{}` | Pre-set filters |

## Styling

The component uses Tailwind CSS classes and includes:
- Responsive design (mobile-first)
- Smooth animations and transitions
- Consistent color scheme
- Accessible form elements
- Custom scrollbars for filter sections

## Integration with Backend

The component works with the optimized search service backend:

### Text Search
```javascript
POST /api/search/text
{
  "query": "laptop",
  "category": "electronics",
  "limit": 20,
  "offset": 0
}
```

### Image Search
```javascript
POST /api/search/image
FormData: {
  file: [image file],
  category: "electronics",
  limit: 20,
  offset: 0
}
```

### Hybrid Search
```javascript
POST /api/search/combined
FormData: {
  query: "gaming laptop",
  file: [image file],
  category: "electronics",
  limit: 20,
  offset: 0
}
```

### Advanced Search
```javascript
POST /api/search/advanced
{
  "mode": "hybrid",
  "query": "laptop",
  "filters": {
    "categories": ["electronics"],
    "brands": ["Apple", "Dell"],
    "min_price": 500,
    "max_price": 2000,
    "in_stock": true,
    "min_rating": 4
  }
}
```

## Mobile Responsiveness

The interface adapts to different screen sizes:

- **Desktop**: Full horizontal layout with side-by-side components
- **Tablet**: Stacked layout with maintained functionality
- **Mobile**: Single-column layout with touch-optimized controls

## Accessibility

- Keyboard navigation support
- Screen reader friendly
- High contrast mode support
- Focus management
- ARIA labels and descriptions

## Performance Optimizations

- Debounced autocomplete
- Lazy loading of categories
- Optimized re-renders with React.memo
- Image compression on upload
- Efficient state management

## Error Handling

The component handles various error scenarios:
- Invalid file types/sizes
- Network failures
- Backend errors
- Missing required fields
- Rate limiting

## Customization

### Theme Colors
Modify the Tailwind color classes:
```css
/* Primary colors */
.bg-blue-600 -> .bg-purple-600
.text-blue-600 -> .text-purple-600

/* Secondary colors */
.bg-gray-50 -> .bg-slate-50
```

### Filter Options
Extend the filter arrays:
```javascript
const PRICE_RANGES = [
  { label: 'Under $25', min: 0, max: 25 },
  { label: '$25 - $50', min: 25, max: 50 },
  // Add more ranges
];
```

### Search Modes
Add new search modes by extending the enum:
```javascript
const SEARCH_MODES = {
  TEXT: 'text',
  IMAGE: 'image',
  HYBRID: 'hybrid',
  VOICE: 'voice', // New mode
};
```

## Best Practices

1. **Always handle errors gracefully**
2. **Provide clear loading feedback**
3. **Validate inputs before submission**
4. **Use debouncing for real-time features**
5. **Implement proper analytics tracking**
6. **Test on multiple devices and browsers**
7. **Follow accessibility guidelines**

## Future Enhancements

- Voice search integration
- Barcode scanning
- Advanced ML-based recommendations
- Social sharing of searches
- Search history and favorites
- Collaborative filtering
- Real-time search suggestions
- AR-based product discovery
