import api from './api';

/**
 * Get all available stock lists
 * @returns {Promise} Promise with stock lists data
 */
export const getStockLists = async () => {
  try {
    const response = await api.get('/stock-lists');
    return response.data;
  } catch (error) {
    console.error('Error fetching stock lists:', error);
    throw error;
  }
};

/**
 * Get stocks for a specific list
 * @param {string} listId - ID of the stock list
 * @returns {Promise} Promise with stocks data
 */
export const getStockList = async (listId) => {
  try {
    const response = await api.get(`/stock-lists/${listId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching stock list ${listId}:`, error);
    throw error;
  }
};

/**
 * Upload a custom stock list
 * @param {File} file - CSV file with stock list
 * @returns {Promise} Promise with upload result
 */
export const uploadCustomList = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/stock-lists/custom', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error uploading custom list:', error);
    throw error;
  }
};