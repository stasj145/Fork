/**
 * User API types
 * These types match the backend schemas for user endpoints
 */

// ============================================================================
// SHARED TYPES
// ============================================================================

export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
}

export enum ActivityLevels {
  SEDENTARY = 'sedentary',
  LIGHTLY_ACTIVE = 'lightly_active',
  MODERATELY_ACTIVE = 'moderately_active',
  VERY_ACTIVE = 'very_active',
  SUPER_ACTIVE = 'super_active',
}

export interface GoalsBase {
  daily_calorie_target: number
  daily_protein_target: number
  daily_carbs_target: number
  daily_fat_target: number
  daily_calorie_burn_target: number
}

export interface WeightHistory {
  id?: string
  weight: number
  created_at: string
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface UserCreateRequest {
  username: string
  email: string
  password: string
  goals?: GoalsBase
  weight_history?: WeightHistory[]
  height?: number
  age?: number
  gender?: Gender
  activity_level?: ActivityLevels
}

export interface UserUpdateRequest {
  username?: string
  email?: string
  password?: string
  goals?: GoalsBase
  weight?: number
  height?: number
  age?: number
  gender?: Gender
  activity_level?: ActivityLevels
  onboarding_finished?: boolean
}

export interface WeightHistoryUpdateRequest {
  weightHistory: WeightHistory[]
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface UserInDB {
  id: string
  username: string
  email: string
  goals: GoalsBase
  weight_history: WeightHistory[]
  height: number
  age: number
  gender: Gender
  activity_level: ActivityLevels
  onboarding_finished: boolean
}