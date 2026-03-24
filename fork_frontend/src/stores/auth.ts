import { defineStore } from 'pinia'
import { AuthService } from '@/services/authService'
import type { TokenResponse } from '@/types/api/auth.types'
import type { UserCreateRequest, UserInDB } from '@/types/api/user.types'

interface AuthState {
  user: TokenResponse | null
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
        const authService = new AuthService()
        const response: TokenResponse = await authService.login({ username, password })

        this.user = response
        localStorage.setItem('user', JSON.stringify(response))

        return response
      } catch (error) {
        // If login fails, remove any existing user data
        this.logout()
        throw error
      }
    },
    async register(userData: UserCreateRequest) {
      try {
        const authService = new AuthService()
        const user: UserInDB = await authService.register(userData)
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
