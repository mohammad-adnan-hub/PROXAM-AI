export const USER_ROLES = {
  STUDENT: 'student',
  TEACHER: 'teacher',
  ADMIN: 'admin',
}

export const ROUTES = {
  // Public
  HOME: '/',
  ABOUT: '/about',
  HELP: '/help',

  // Auth
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',

  // Student
  STUDENT_DASHBOARD: '/student/dashboard',
  STUDENT_ENTER_CODE: '/student/enter-code',
  STUDENT_TEST_DETAILS: '/student/tests/:testId',
  STUDENT_SYSTEM_CHECK: '/student/tests/:testId/system-check',
  STUDENT_VERIFICATION: '/student/tests/:testId/verification',
  STUDENT_EXAM: '/student/attempts/:attemptId/exam',
  STUDENT_SUBMITTED: '/student/attempts/:attemptId/submitted',
  STUDENT_RESULT: '/student/attempts/:attemptId/result',
  STUDENT_HISTORY: '/student/history',
  STUDENT_PROFILE: '/student/profile',

  // Teacher
  TEACHER_DASHBOARD: '/teacher/dashboard',
  TEACHER_TESTS: '/teacher/tests',
  TEACHER_CREATE_DETAILS: '/teacher/tests/create',
  TEACHER_CREATE_QUESTIONS: '/teacher/tests/create/questions',
  TEACHER_CREATE_PREVIEW: '/teacher/tests/create/preview',
  TEACHER_TEST_DETAILS: '/teacher/tests/:testId',
  TEACHER_TEST_SUCCESS: '/teacher/tests/:testId/created',
  TEACHER_ATTEMPTS: '/teacher/tests/:testId/attempts',
  TEACHER_REVIEW: '/teacher/attempts/:attemptId/review',
  TEACHER_PROFILE: '/teacher/profile',

  // Admin
  ADMIN_DASHBOARD: '/admin/dashboard',
  ADMIN_USERS: '/admin/users',
  ADMIN_USER_DETAILS: '/admin/users/:userId',
  ADMIN_TESTS: '/admin/tests',
  ADMIN_TEST_DETAILS: '/admin/tests/:testId',
  ADMIN_PROCTORING: '/admin/proctoring-alerts',
  ADMIN_PROFILE: '/admin/profile',

  // System
  NOT_FOUND: '/404',
  UNAUTHORIZED: '/unauthorized',
}

export const PROCTORING_EVENT_LABELS = {
  face_not_detected: 'Face not detected',
  multiple_faces_detected: 'Multiple faces detected',
  looking_away: 'Looking away',
  fullscreen_exited: 'Fullscreen exited',
  tab_visibility_changed: 'Tab switched',
  camera_disconnected: 'Camera disconnected',
  microphone_unavailable: 'Microphone unavailable',
  network_interrupted: 'Network interrupted',
  identity_check_failed: 'Identity check failed',
}

export const REVIEW_STATUS_LABELS = {
  unreviewed: 'Unreviewed',
  under_review: 'Under Review',
  reviewed: 'Reviewed',
  no_concern: 'No Concern',
  requires_further_review: 'Requires Further Review',
}
