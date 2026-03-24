import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { LoginRequest, TokenResponse } from '@/types/api/auth.types'

export class AuthService {
  private readonly BASE_URL = '/api/v1/auth'

  async login(credentials: { username: string; password: string }): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    formData.append('grant_type', 'password')

    return fetchWrapper.post(`${this.BASE_URL}/login`, formData)
  }
}