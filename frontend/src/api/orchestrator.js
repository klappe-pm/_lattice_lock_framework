import { apiClient } from './client';

/**
 * Orchestrator API
 * Handles prompt execution and chain operations
 */

export const orchestratorApi = {
  /**
   * Execute a prompt with optional system instructions
   * @param {Object} request - Execution request
   * @param {string} request.prompt - User prompt
   * @param {string} request.system_instructions - Optional system instructions
   * @param {string} request.model - Optional specific model to use
   * @param {Object} request.options - Additional options
   * @returns {Promise<Object>} Execution result
   */
  async execute(request) {
    return apiClient.post('/orchestrator/execute', request);
  },

  /**
   * Execute a chain of models
   * @param {Object} request - Chain request
   * @param {string} request.prompt - Initial prompt
   * @param {Array<string>} request.chain - Ordered list of models
   * @returns {Promise<Object>} Chain execution result
   */
  async executeChain(request) {
    return apiClient.post('/orchestrator/chain', request);
  },

  /**
   * Execute with consensus from multiple models
   * @param {Object} request - Consensus request
   * @param {string} request.prompt - User prompt
   * @param {Array<string>} request.models - Models to query
   * @returns {Promise<Object>} Consensus result
   */
  async executeConsensus(request) {
    return apiClient.post('/orchestrator/consensus', request);
  },

  /**
   * Get model selection analysis for a prompt
   * @param {string} prompt - User prompt to analyze
   * @returns {Promise<Object>} Selection analysis with routing info
   */
  async analyzeSelection(prompt) {
    return apiClient.post('/orchestrator/analyze', { prompt });
  },

  /**
   * Get execution history
   * @param {Object} options - Query options
   * @param {number} options.limit - Max results
   * @param {number} options.offset - Pagination offset
   * @returns {Promise<Array>} Execution history
   */
  async getHistory(options = {}) {
    const params = new URLSearchParams(options);
    return apiClient.get(`/orchestrator/history?${params}`);
  },

  /**
   * Get execution details by ID
   * @param {string} id - Execution ID
   * @returns {Promise<Object>} Full execution details
   */
  async getExecution(id) {
    return apiClient.get(`/orchestrator/executions/${id}`);
  },
};

export default orchestratorApi;
