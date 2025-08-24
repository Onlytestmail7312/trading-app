import api from './api';

/**
 * Scan for trading opportunities using a specific strategy
 * @param {Object} scanConfig - Scan configuration
 * @param {string} scanConfig.strategy_id - ID of the strategy
 * @param {string} scanConfig.stock_list_id - ID of the stock list
 * @param {Array} scanConfig.stocks - Array of stock symbols (optional)
 * @param {Object} scanConfig.parameters - Strategy parameters
 * @returns {Promise} Promise with trading opportunities
 */
export const scanForOpportunities = async (scanConfig) => {
  try {
    const response = await api.post('/monitoring/scan', scanConfig);
    return response.data;
  } catch (error) {
    console.error('Error scanning for opportunities:', error);
    throw error;
  }
};

/**
 * Set up daily monitoring for trading opportunities
 * @param {Object} monitoringConfig - Monitoring configuration
 * @param {string} monitoringConfig.strategy_id - ID of the strategy
 * @param {string} monitoringConfig.stock_list_id - ID of the stock list
 * @param {Array} monitoringConfig.stocks - Array of stock symbols (optional)
 * @param {Object} monitoringConfig.parameters - Strategy parameters
 * @param {string} monitoringConfig.notification_email - Email for notifications (optional)
 * @param {string} monitoringConfig.notification_time - Time for notifications (optional)
 * @returns {Promise} Promise with monitoring setup details
 */
export const setupMonitoring = async (monitoringConfig) => {
  try {
    const response = await api.post('/monitoring/setup', monitoringConfig);
    return response.data;
  } catch (error) {
    console.error('Error setting up monitoring:', error);
    throw error;
  }
};

/**
 * Get all monitoring setups for the current user
 * @returns {Promise} Promise with monitoring setups
 */
export const getMonitoringSetups = async () => {
  try {
    const response = await api.get('/monitoring');
    return response.data;
  } catch (error) {
    console.error('Error fetching monitoring setups:', error);
    throw error;
  }
};

/**
 * Delete a monitoring setup
 * @param {string} monitoringId - ID of the monitoring setup
 * @returns {Promise} Promise with deletion status
 */
export const deleteMonitoring = async (monitoringId) => {
  try {
    const response = await api.delete(`/monitoring/${monitoringId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting monitoring setup ${monitoringId}:`, error);
    throw error;
  }
};

/**
 * Get recent alerts for the current user
 * @returns {Promise} Promise with alerts
 */
export const getAlerts = async () => {
  try {
    const response = await api.get('/monitoring/alerts');
    return response.data;
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
};