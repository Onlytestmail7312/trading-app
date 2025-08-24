import api from './api';

/**
 * Run a backtest for a specific strategy on selected stocks
 * @param {Object} backtestConfig - Backtest configuration
 * @param {string} backtestConfig.strategy_id - ID of the strategy
 * @param {string} backtestConfig.stock_list_id - ID of the stock list
 * @param {Array} backtestConfig.stocks - Array of stock symbols (optional)
 * @param {string} backtestConfig.start_date - Start date (YYYY-MM-DD)
 * @param {string} backtestConfig.end_date - End date (YYYY-MM-DD)
 * @param {number} backtestConfig.initial_capital - Initial capital
 * @param {Object} backtestConfig.parameters - Strategy parameters
 * @returns {Promise} Promise with backtest results
 */
export const runBacktest = async (backtestConfig) => {
  try {
    const response = await api.post('/backtest', backtestConfig);
    return response.data;
  } catch (error) {
    console.error('Error running backtest:', error);
    throw error;
  }
};

/**
 * Get results for a specific backtest
 * @param {string} backtestId - ID of the backtest
 * @returns {Promise} Promise with backtest results
 */
export const getBacktestResults = async (backtestId) => {
  try {
    const response = await api.get(`/backtest/${backtestId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching backtest results ${backtestId}:`, error);
    throw error;
  }
};

/**
 * Get history of backtests for the current user
 * @returns {Promise} Promise with backtest history
 */
export const getBacktestHistory = async () => {
  try {
    const response = await api.get('/backtest/history');
    return response.data;
  } catch (error) {
    console.error('Error fetching backtest history:', error);
    throw error;
  }
};