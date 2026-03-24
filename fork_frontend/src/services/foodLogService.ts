import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type {
  FoodEntryCreateRequest,
  FoodEntryUpdateRequest,
  FoodEntryInDB,
  LogInDB,
} from '@/types/api/foodLog.types'

export class FoodLogService {
  private readonly BASE_URL = '/api/v1/log'

  async getOrCreateLog(date: string): Promise<LogInDB> {
    return fetchWrapper.get(`${this.BASE_URL}/day/${date}/food`)
  }

  async addFoodToLog(date: string, foodEntryData: FoodEntryCreateRequest): Promise<FoodEntryInDB> {
    return fetchWrapper.post(`${this.BASE_URL}/day/${date}/food`, foodEntryData)
  }

  async removeFoodEntry(date: string, foodEntryId: string): Promise<void> {
    return fetchWrapper.delete(`${this.BASE_URL}/day/${date}/food/${foodEntryId}`)
  }

  async updateFoodEntry(
    date: string,
    foodEntryId: string,
    foodEntryData: FoodEntryUpdateRequest
  ): Promise<FoodEntryInDB> {
    return fetchWrapper.patch(`${this.BASE_URL}/day/${date}/food/${foodEntryId}`, foodEntryData)
  }

  async getLastLogs(nLogs: number = 1): Promise<LogInDB[]> {
    return fetchWrapper.get(`${this.BASE_URL}/last/food?n_logs=${nLogs}`)
  }
}