import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { LoginRequest, TokenResponse } from '@/types/api/auth.types'
import type { UserCreateRequest, UserInDB } from '@/types/api/user.types'

export class AuthService {
  private readonly BASE_URL = '/api/v1'

  async login(credentials: { username: string; password: string }): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    formData.append('grant_type', 'password')

    return fetchWrapper.post(`${this.BASE_URL}/auth/login`, formData)
  }

  async register(userData: UserCreateRequest): Promise<UserInDB> {
    return fetchWrapper.post(`${this.BASE_URL}/user/`, userData)
  }
}
