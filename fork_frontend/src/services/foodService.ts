import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type {
  FoodCreateRequest,
  FoodUpdateRequest,
  FoodDetailed,
  FoodSearchRequest,
  ImageUrlRequest,
  RequestImage,
  ImageSize,
} from '@/types/api/food.types'

export class FoodService {
  private readonly BASE_URL = '/api/v1/food'

  async createFood(foodData: FoodCreateRequest): Promise<FoodDetailed> {
    return fetchWrapper.post(`${this.BASE_URL}/item/`, foodData)
  }

  async getFood(foodId: string): Promise<FoodDetailed> {
    return fetchWrapper.get(`${this.BASE_URL}/item/${foodId}`)
  }

  async updateFood(foodId: string, foodData: FoodUpdateRequest): Promise<FoodDetailed> {
    return fetchWrapper.patch(`${this.BASE_URL}/item/${foodId}`, foodData)
  }

  async deleteFood(foodId: string): Promise<void> {
    return fetchWrapper.delete(`${this.BASE_URL}/item/${foodId}`)
  }

  async searchFood(searchParams: FoodSearchRequest): Promise<FoodDetailed[]> {
    return fetchWrapper.post(`${this.BASE_URL}/search`, searchParams)
  }

  async getLastLogged(nItems: number): Promise<FoodDetailed[]> {
    return fetchWrapper.get(`${this.BASE_URL}/last_logged?n_items=${nItems}`)
  }

  async updateFoodImage(foodId: string, file: File): Promise<RequestImage> {
    const formData = new FormData()
    formData.append('file', file)
    return fetchWrapper.put(`${this.BASE_URL}/item/${foodId}/image`, formData)
  }

  async updateFoodImageFromUrl(
    foodId: string,
    imageUrl: ImageUrlRequest
  ): Promise<RequestImage> {
    return fetchWrapper.put(`${this.BASE_URL}/item/${foodId}/image_from_url`, imageUrl)
  }

  async getFoodImage(foodId: string, size: ImageSize = 'thumbnail'): Promise<ArrayBuffer> {
    return fetchWrapper.get(`${this.BASE_URL}/item/${foodId}/image?size=${size}`)
  }

  async deleteFoodImage(foodId: string): Promise<void> {
    return fetchWrapper.delete(`${this.BASE_URL}/item/${foodId}/image`)
  }
}