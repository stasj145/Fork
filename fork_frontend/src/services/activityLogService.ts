import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type {
  ActivityEntryCreateRequest,
  ActivityEntryUpdateRequest,
  ActivityEntryInDB,
  ActivityLogInDB,
} from '@/types/api/activityLog.types'

export class ActivityLogService {
  private readonly BASE_URL = '/api/v1/log'

  async getOrCreateLog(date: string): Promise<ActivityLogInDB> {
    return fetchWrapper.get(`${this.BASE_URL}/day/${date}/activity`)
  }

  async addActivityToLog(
    date: string,
    activityEntryData: ActivityEntryCreateRequest
  ): Promise<ActivityEntryInDB> {
    return fetchWrapper.post(`${this.BASE_URL}/day/${date}/activity`, activityEntryData)
  }

  async removeActivityEntry(date: string, activityEntryId: string): Promise<void> {
    return fetchWrapper.delete(`${this.BASE_URL}/day/${date}/activity/${activityEntryId}`)
  }

  async updateActivityEntry(
    date: string,
    activityEntryId: string,
    activityEntryData: ActivityEntryUpdateRequest
  ): Promise<ActivityEntryInDB> {
    return fetchWrapper.patch(
      `${this.BASE_URL}/day/${date}/activity/${activityEntryId}`,
      activityEntryData
    )
  }

  async getLastLogs(nLogs: number = 1): Promise<ActivityLogInDB[]> {
    return fetchWrapper.get(`${this.BASE_URL}/last/activity?n_logs=${nLogs}`)
  }
}