import api from './api'

const VALIDATION_TOKEN_KEY = 'proxam_ai_validation_token'

export const studentService = {
  /**
   * Validate a student examination code and return sanitized test details.
   * Never exposes questions, options, correct answers, or teacher information.
   * Stores the validation token in sessionStorage for subsequent requests.
   * @param {string} testCode
   * @returns {Promise<Object>} Sanitized test details
   */
  async validateTestCode(testCode) {
    const response = await api.post('/student/tests/validate-code', {
      test_code: testCode,
    })
    const data = response.data
    if (data.validation_token) {
      sessionStorage.setItem(VALIDATION_TOKEN_KEY, data.validation_token)
    }
    return data
  },

  /**
   * Clear the stored validation token from sessionStorage.
   */
  clearValidationToken() {
    sessionStorage.removeItem(VALIDATION_TOKEN_KEY)
  },

  /**
   * Get the stored validation token from sessionStorage.
   * @returns {string|null}
   */
  getValidationToken() {
    return sessionStorage.getItem(VALIDATION_TOKEN_KEY)
  },

  /**
   * Get sanitized examination details by ID for an authenticated student.
   * Sends the stored validation token via X-Validation-Token header.
   * @param {number|string} testId
   * @returns {Promise<Object>} Sanitized test details
   */
  async getStudentTestDetails(testId) {
    const token = sessionStorage.getItem(VALIDATION_TOKEN_KEY)
    const headers = {}
    if (token) {
      headers['X-Validation-Token'] = token
    }
    const response = await api.get(`/student/tests/${testId}`, { headers })
    return response.data
  },

  /**
   * Create a new examination attempt for the authenticated student.
   * Does not start the examination timer.
   * @param {number|string} testId
   * @returns {Promise<Object>} Created attempt details
   */
  async createAttempt(testId) {
    const response = await api.post(`/student/tests/${testId}/attempt`)
    return response.data
  },

  /**
   * Start an examination attempt. Transitions status to in_progress
   * and initializes the server-side timer.
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Started attempt details
   */
  async startAttempt(attemptId) {
    const response = await api.post(`/student/attempts/${attemptId}/start`)
    return response.data
  },

  /**
   * Retrieve questions for an in_progress attempt.
   * Correct answers are excluded from the response.
   * @param {number|string} attemptId
   * @returns {Promise<Array>} List of questions with options (no correct answers)
   */
  async getAttemptQuestions(attemptId) {
    const response = await api.get(`/student/attempts/${attemptId}/questions`)
    return response.data
  },

  /**
   * Fetch all saved answers for an attempt.
   * @param {number|string} attemptId
   * @returns {Promise<Array>} List of saved answers
   */
  async getSavedAnswers(attemptId) {
    const response = await api.get(`/student/attempts/${attemptId}/answers`)
    return response.data
  },

  /**
   * Save or update a student's answer for a question.
   * @param {number|string} attemptId
   * @param {number|string} questionId
   * @param {number|null} selectedOptionId
   * @param {boolean} isMarkedForReview
   * @returns {Promise<Object>} Saved answer details
   */
  async saveAnswer(attemptId, questionId, selectedOptionId, isMarkedForReview = false) {
    const response = await api.put(
      `/student/attempts/${attemptId}/answers/${questionId}`,
      { selected_option_id: selectedOptionId, is_marked_for_review: isMarkedForReview },
    )
    return response.data
  },

  /**
   * Clear a student's answer for a question (deselect the option).
   * Preserves mark-for-review status.
   * @param {number|string} attemptId
   * @param {number|string} questionId
   * @returns {Promise<Object>} Clear result
   */
  async clearAnswer(attemptId, questionId) {
    const response = await api.delete(
      `/student/attempts/${attemptId}/answers/${questionId}`,
    )
    return response.data
  },

  /**
   * Submit an examination attempt for final scoring.
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Finalized attempt and result details
   */
  async submitAttempt(attemptId) {
    const response = await api.post(`/student/attempts/${attemptId}/submit`)
    return response.data
  },

  /**
   * Fetch the calculated result for a finalized attempt.
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Result details
   */
  async getAttemptResult(attemptId) {
    const response = await api.get(`/student/attempts/${attemptId}/result`)
    return response.data
  },

  /**
   * Fetch the authenticated student's examination attempts,
   * ordered newest first.
   * @returns {Promise<Array>} List of attempt history items with results where available
   */
  async getStudentAttempts() {
    const response = await api.get('/student/attempts')
    return response.data
  },

  /**
   * Record a browser-detected proctoring event for an active examination attempt.
   * @param {number|string} attemptId
   * @param {Object} eventData
   * @returns {Promise<Object>} Created proctoring event details
   */
  async recordProctoringEvent(attemptId, eventData) {
    const response = await api.post(
      `/student/attempts/${attemptId}/proctoring-events`,
      eventData,
    )
    return response.data
  },

  /**
   * Get identity verification status for the authenticated student's attempt.
   * @param {number|string} attemptId
   * @returns {Promise<Object>} Identity verification status details
   */
  async getIdentityVerificationStatus(attemptId) {
    const response = await api.get(`/student/attempts/${attemptId}/identity-verification`)
    return response.data
  },

  /**
   * Submit a one-time identity photograph for manual review.
   * @param {number|string} attemptId
   * @param {Blob|File} photoBlob
   * @returns {Promise<Object>} Submission result (status pending, not auto-verified)
   */
  async submitIdentityVerification(attemptId, photoBlob) {
    const formData = new FormData()
    const file =
      photoBlob instanceof File
        ? photoBlob
        : new File([photoBlob], 'identity-photo.jpg', { type: photoBlob?.type || 'image/jpeg' })
    formData.append('photo', file)
    // Let the browser/axios set multipart boundary automatically.
    const response = await api.post(
      `/student/attempts/${attemptId}/identity-verification`,
      formData,
      { headers: { 'Content-Type': undefined } }
    )
    return response.data
  },

}

export default studentService
