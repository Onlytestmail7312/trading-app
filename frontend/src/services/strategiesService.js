import api from './api';

/**
 * Get all available trading strategies
 * @returns {Promise} Promise with strategies data
 */
export const getStrategies = async () => {
  try {
    const response = await api.get('/strategies');
    return response.data;
  } catch (error) {
    console.error('Error fetching strategies:', error);
    throw error;
  }
};

/**
 * Get details for a specific strategy
 * @param {string} strategyId - ID of the strategy
 * @returns {Promise} Promise with strategy details
 */
export const getStrategy = async (strategyId) => {
  try {
    const response = await api.get(`/strategies/${strategyId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching strategy ${strategyId}:`, error);
    throw error;
  }
};

/**
 * Get parameters for a specific strategy
 * @param {string} strategyId - ID of the strategy
 * @returns {Promise} Promise with strategy parameters
 */
export const getStrategyParameters = async (strategyId) => {
  try {
    const response = await api.get(`/strategies/${strategyId}/parameters`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching parameters for strategy ${strategyId}:`, error);
    throw error;
  }
};