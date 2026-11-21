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
   * Get attempts for a test (teacher).
   * @param {number|string} testId
   * @returns {Promise<Array>} List of attempts
   */
  async getTestAttempts(testId) {
    const response = await api.get(`/teacher/tests/${testId}/attempts`)
    return response.data
  },

  /**
   * Get attempt detail (teacher).
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Attempt detail
   */
  async getTeacherAttempt(attemptId) {
    const response = await api.get(`/teacher/attempts/${attemptId}`)
    return response.data
  },

  /**
   * Review a proctoring event (teacher).
   * @param {number|string} attemptId
   * @param {number|string} eventId
   * @param {Object} payload - { review_status, reviewer_notes }
   * @returns {Promise<Object>} Updated proctoring event
   */
  async reviewProctoringEvent(attemptId, eventId, payload) {
    const response = await api.put(`/proctoring/attempts/${attemptId}/events/${eventId}`, payload)
    return response.data
  },

  /**
   * Get proctoring events for an attempt (teacher).
   * @param {number|string} attemptId
   * @returns {Promise<Array>} List of proctoring events
   */
  async getProctoringEvents(attemptId) {
    const response = await api.get(`/proctoring/attempts/${attemptId}/events`)
    return response.data
  },

  /**
   * Get attempt result (teacher).
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Result details
   */
  async getTeacherAttemptResult(attemptId) {
    const response = await api.get(`/teacher/attempts/${attemptId}/result`)
    return response.data
  },
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

  /**
   * Get identity verification records for a teacher's examination.
   * @param {number|string} testId
   * @returns {Promise<Array>} List of identity verification records
   */
  async getTestIdentityVerifications(testId) {
    const response = await api.get(`/teacher/tests/${testId}/identity-verifications`)
    return response.data
  },

  /**
   * Get a specific identity verification record for teacher review.
   * @param {number|string} verificationId
   * @returns {Promise<Object>} Identity verification record with student info
   */
  async getIdentityVerificationForReview(verificationId) {
    const response = await api.get(`/teacher/identity-verifications/${verificationId}`)
    return response.data
  },

  /**
   * Get the identity verification image for teacher review.
   * @param {number|string} verificationId
   * @returns {Promise<Blob>} Identity photograph blob
   */
  async getIdentityVerificationImage(verificationId) {
    const response = await api.get(
      `/teacher/identity-verifications/${verificationId}/image`,
      { responseType: 'blob' }
    )
    return response.data
  },

  /**
   * Approve or reject an identity verification record.
   * @param {number|string} verificationId
   * @param {Object} payload - { status: 'verified'|'rejected', reviewer_notes?: string }
   * @returns {Promise<Object>} Updated identity verification record
   */
  async reviewIdentityVerification(verificationId, payload) {
    const response = await api.put(
      `/teacher/identity-verifications/${verificationId}`,
      payload
    )
    return response.data
  },
}

export default testService
