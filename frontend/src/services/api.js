import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend service is unavailable');
  }
};

// Advanced search with filters
export const advancedSearch = async (searchParams) => {
  try {
    const { mode, query, image, filters } = searchParams;

    // Build the request based on search mode
    let endpoint = '/search/advanced';
    let requestData;
    let config = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (mode === 'image') {
      // For image or hybrid search, use FormData
      const formData = new FormData();

      if (image) {
        formData.append('file', image);
      }

      if (query && (mode === 'text' || mode === 'hybrid')) {
        formData.append('query', query);
      }

      // Add filters as JSON string
      formData.append('filters', JSON.stringify(filters));
      formData.append('mode', mode);

      requestData = formData;
      config.headers['Content-Type'] = 'multipart/form-data';

    } else {
      // For text-only search, use JSON
      requestData = {
        query,
        filters,
        mode
      };
    }

    const response = await api.post(endpoint, requestData, config);
    return response.data;

  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Advanced search failed');
  }
};

// Text search
export const searchByText = async (query, category = '', limit = 20, offset = 0) => {
  try {
    const response = await api.post('/search/text', {
      query,
      category: category || undefined,
      limit,
      offset
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Text search failed');
  }
};

// Image search
export const searchByImage = async (imageFile, category = '', limit = 20, offset = 0) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);

    // Add other parameters as query params since this is a file upload
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await api.post(`/search/image?${params.toString()}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Image search failed');
  }
};

// Combined search (text + image)
export const searchCombined = async (query, imageFile, category = '', limit = 20, offset = 0) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('query', query);
    if (category) formData.append('category', category);
    formData.append('limit', limit.toString());
    formData.append('offset', offset.toString());

    const response = await api.post('/search/combined', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Combined search failed');
  }
};

// Get similar products
export const getSimilarProducts = async (productId, limit = 10) => {
  try {
    const response = await api.get(`/search/similar/${productId}?limit=${limit}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get similar products');
  }
};

// Get categories
export const getCategories = async () => {
  try {
    const response = await api.get('/products/categories');
    return response.data.categories;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get categories');
  }
};

// Upload image (standalone)
export const uploadImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Image upload failed');
  }
};

export default api;
