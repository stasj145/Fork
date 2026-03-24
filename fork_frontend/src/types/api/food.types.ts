/**
 * Food API types
 * These types match the backend schemas for food endpoints
 */

// ============================================================================
// SHARED TYPES
// ============================================================================

export type FoodSources = 'local' | 'personal' | 'openfoodfacts' | 'tandoor'

export type ImageSize = 'large' | 'thumbnail'

interface _BaseFood {
  name: string
  brand: string
  description: string
  serving_size: number
  serving_unit: string
  calories_per_100: number
  protein_per_100: number
  carbs_per_100: number
  fat_per_100: number
  private: boolean
  hidden: boolean
  barcode: string | null
}

export interface FoodIngredientInDB {
  quantity: number
  parent_id: string
  ingredient_id: string
  ingredient?: FoodInDB | null
}

export interface FoodInDB extends _BaseFood {
  id: string
  img_name: string | null
}

export interface FoodDetailed extends FoodInDB {
  ingredients: FoodIngredientInDB[]
  external_image_url: string | null
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface FoodIngredientCreate {
  parent_id?: string
  ingredient_id: string
  quantity: number
}

export interface FoodCreateRequest extends Partial<_BaseFood>{
  name: string
  ingredients?: FoodIngredientCreate[]
}

export interface FoodUpdateRequest extends Partial<_BaseFood>{
  ingredients?: FoodIngredientCreate[]
}

export interface FoodSearchRequest {
  query?: string
  code?: string
  source?: FoodSources
  limit?: number
}

export interface ImageUrlRequest {
  url: string
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface RequestImage {
  name: string
}