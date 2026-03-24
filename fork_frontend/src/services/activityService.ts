import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type {
  ActivityCreateRequest,
  ActivityUpdateRequest,
  ActivityDetailed,
  ActivitySearchRequest,
} from '@/types/api/activity.types'

export class ActivityService {
  private readonly BASE_URL = '/api/v1/activity'

  async createActivity(activityData: ActivityCreateRequest): Promise<ActivityDetailed> {
    return fetchWrapper.post(`${this.BASE_URL}/item/`, activityData)
  }

  async getActivity(activityId: string): Promise<ActivityDetailed> {
    return fetchWrapper.get(`${this.BASE_URL}/item/${activityId}`)
  }

  async updateActivity(
    activityId: string,
    activityData: ActivityUpdateRequest
  ): Promise<ActivityDetailed> {
    return fetchWrapper.patch(`${this.BASE_URL}/item/${activityId}`, activityData)
  }

  async deleteActivity(activityId: string): Promise<void> {
    return fetchWrapper.delete(`${this.BASE_URL}/item/${activityId}`)
  }

  async searchActivities(searchParams: ActivitySearchRequest): Promise<ActivityDetailed[]> {
    return fetchWrapper.post(`${this.BASE_URL}/search`, searchParams)
  }

  async getLastLogged(nItems: number): Promise<ActivityDetailed[]> {
    return fetchWrapper.get(`${this.BASE_URL}/last_logged?n_items=${nItems}`)
  }
}