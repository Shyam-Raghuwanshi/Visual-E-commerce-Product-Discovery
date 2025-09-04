import { useState, useCallback } from 'react';
import { searchByText, searchByImage, searchCombined, advancedSearch } from '../services/api';
import toast from 'react-hot-toast';

export const useSearch = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const performSearch = useCallback(async (searchParams) => {
    setIsLoading(true);
    setError(null);

    try {
      const { mode, query, image, filters } = searchParams;
      let results;

      // Use advanced search if filters are provided
      if (filters && (
        filters.categories?.length > 0 ||
        filters.brands?.length > 0 ||
        filters.priceRange ||
        filters.minPrice ||
        filters.maxPrice ||
        filters.inStockOnly ||
        filters.minRating > 0
      )) {
        results = await advancedSearch(searchParams);
      } else {
        // Use simple search APIs for better performance
        switch (mode) {
          case 'text':
            results = await searchByText(
              query,
              filters?.categories?.[0] || '',
              20,
              0
            );
            break;

          case 'image':
            results = await searchByImage(
              image,
              filters?.categories?.[0] || '',
              20,
              0
            );
            break;

          case 'hybrid':
            results = await searchCombined(
              query,
              image,
              filters?.categories?.[0] || '',
              20,
              0
            );
            break;

          default:
            throw new Error('Invalid search mode');
        }
      }

      setIsLoading(false);
      return results;

    } catch (err) {
      const errorMessage = err.message || 'Search failed. Please try again.';
      setError(errorMessage);
      setIsLoading(false);
      toast.error(errorMessage);
      throw err;
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    performSearch,
    isLoading,
    error,
    clearError
  };
};

export default useSearch;
