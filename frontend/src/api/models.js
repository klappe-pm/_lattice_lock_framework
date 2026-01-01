import { apiClient } from './client';

/**
 * Model Registry API
 * Handles CRUD operations for model configurations
 */

export const modelsApi = {
  /**
   * Get all registered models
   * @returns {Promise<Array>} List of models with masked keys
   */
  async getAll() {
    return apiClient.get('/models');
  },

  /**
   * Get a single model by ID
   * @param {string} id - Model ID
   * @returns {Promise<Object>} Model details
   */
  async getById(id) {
    return apiClient.get(`/models/${id}`);
  },

  /**
   * Register a new model
   * @param {Object} model - Model configuration
   * @param {string} model.name - Display name
   * @param {string} model.provider - Provider (openai, anthropic, etc.)
   * @param {string} model.api_name - API model name
   * @param {string} model.api_key - API key (sent once, stored encrypted)
   * @param {Array<string>} model.capabilities - Model capabilities
   * @param {number} model.context_window - Context window size
   * @returns {Promise<Object>} Created model
   */
  async create(model) {
    return apiClient.post('/models', model);
  },

  /**
   * Update an existing model
   * @param {string} id - Model ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} Updated model
   */
  async update(id, updates) {
    return apiClient.put(`/models/${id}`, updates);
  },

  /**
   * Delete a model
   * @param {string} id - Model ID
   * @returns {Promise<void>}
   */
  async delete(id) {
    return apiClient.delete(`/models/${id}`);
  },

  /**
   * Test model connection
   * @param {string} id - Model ID
   * @returns {Promise<Object>} Test result with latency
   */
  async testConnection(id) {
    return apiClient.post(`/models/${id}/test`);
  },

  /**
   * Get available providers
   * @returns {Promise<Array>} List of supported providers
   */
  async getProviders() {
    return apiClient.get('/models/providers');
  },
};

export default modelsApi;
