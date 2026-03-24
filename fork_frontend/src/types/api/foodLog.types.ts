/**
 * Food Log API types
 * These types match the backend schemas for food log endpoints
 */

import type { GoalsBase } from './user.types'
import type { FoodDetailed } from './food.types'

// ============================================================================
// SHARED TYPES
// ============================================================================

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

export interface FoodEntryInDB {
  id: string
  food_item: FoodDetailed
  meal_type: MealType
  quantity: number
}

export interface LogInDB {
  id: string
  date: string
  notes: string | null
  food_entries: FoodEntryInDB[]
  goals: GoalsBase
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface FoodEntryCreateRequest {
  food_id: string
  quantity: number
  meal_type: MealType
}

export interface FoodEntryUpdateRequest {
  meal_type?: MealType | null
  quantity?: number | null
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface FoodEntryInDBResponse extends FoodEntryInDB {}

export interface LogInDBResponse extends LogInDB {}