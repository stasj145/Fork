import { defineStore } from 'pinia'
import { fetchWrapper } from '@/helpers/fetch-wrapper'

export interface User {
  access_token: string
  token_type: string
  user_id: string
}

interface AuthState {
  user: User | null
  returnUrl: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    returnUrl: null,
  }),
  actions: {
    async login(username: string, password: string) {
      try {
        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)

        const response = await fetchWrapper.post('/api/v1/auth/login', formData)

        const user: User = {
          access_token: response.access_token,
          token_type: response.token_type,
          user_id: response.user_id,
        }

        this.user = user

        localStorage.setItem('user', JSON.stringify(user))

        return user
      } catch (error) {
        // If login fails, remove any existing user data
        this.logout()
        throw error
      }
    },
    async register(userData: { username: string; email: string; password: string }) {
      try {
        // Register new user
        const user = await fetchWrapper.post('/api/v1/user/', userData)
        return user
      } catch (error) {
        throw error
      }
    },
    logout() {
      this.user = null
      localStorage.removeItem('user')
    },
  },
})
