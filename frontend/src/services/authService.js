import api from './api'

export const authService = {
  async register(fullName, email, password, role = 'student') {
    const { data } = await api.post('/auth/register', {
      full_name: fullName,
      email,
      password,
      role,
    })
    return data
  },

  async login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    return data
  },

  async logout() {
    await api.post('/auth/logout')
  },

  async getMe() {
    const { data } = await api.get('/auth/me')
    return data
  },

  async forgotPassword(email) {
    const { data } = await api.post('/auth/forgot-password', { email })
    return data
  },

  async resetPassword(token, newPassword) {
    const { data } = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
    return data
  },

  async changePassword(currentPassword, newPassword) {
    const { data } = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return data
  },
}
