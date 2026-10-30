import api from './api'

export const testService = {
  /**
   * Create a new test with questions and options.
   * @param {Object} testData
   * @returns {Promise<Object>} Created test details
   */
  async createTest(testData) {
    const response = await api.post('/tests/', testData)
    return response.data
  },

  /**
   * Get all tests created by the authenticated teacher.
   * @returns {Promise<Array>} List of tests
   */
  async getTeacherTests() {
    const response = await api.get('/tests/')
    return response.data
  },

  /**
   * Get dashboard statistics and recent tests for the authenticated teacher.
   * @returns {Promise<Object>} Stats object
   */
  async getTeacherStats() {
    const response = await api.get('/tests/stats')
    return response.data
  },

  /**
   * Get full details of a specific test by ID.
   * @param {number|string} testId
   * @returns {Promise<Object>} Test detail object
   */
  async getTestDetails(testId) {
    const response = await api.get(`/tests/${testId}`)
    return response.data
  },

  /**
   * Update an existing test (only allowed if no student attempts exist).
   * @param {number|string} testId
   * @param {Object} updateData
   * @returns {Promise<Object>} Updated test detail
   */
  async updateTest(testId, updateData) {
    const response = await api.put(`/tests/${testId}`, updateData)
    return response.data
  },

  /**
   * Delete an existing test (only allowed if no student attempts exist).
   * @param {number|string} testId
   * @returns {Promise<Object>} Success message
   */
  async deleteTest(testId) {
    const response = await api.delete(`/tests/${testId}`)
    return response.data
  },
}

export default testService
