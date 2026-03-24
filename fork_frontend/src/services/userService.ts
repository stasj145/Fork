import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type {
  UserCreateRequest,
  UserUpdateRequest,
  UserInDB,
  WeightHistory,
} from '@/types/api/user.types'

export class UserService {
  private readonly BASE_URL = '/api/v1/user'

  async createUser(userData: UserCreateRequest): Promise<UserInDB> {
    return fetchWrapper.post(`${this.BASE_URL}/`, userData)
  }

  async getUser(userId: string): Promise<UserInDB> {
    return fetchWrapper.get(`${this.BASE_URL}/${userId}`)
  }

  async updateUser(
    userId: string,
    userData: UserUpdateRequest,
    weightDateOverwrite?: string
  ): Promise<UserInDB> {
    const params = new URLSearchParams()
    if (weightDateOverwrite) {
      params.append('weight_date_overwrite', weightDateOverwrite)
    }
    const url = `${this.BASE_URL}/${userId}${weightDateOverwrite ? `?${params.toString()}` : ''}`
    return fetchWrapper.patch(url, userData)
  }

  async updateWeightHistory(
    userId: string,
    weightHistory: WeightHistory[]
  ): Promise<WeightHistory[]> {
    return fetchWrapper.put(`${this.BASE_URL}/${userId}/weight-history`, weightHistory)
  }
}