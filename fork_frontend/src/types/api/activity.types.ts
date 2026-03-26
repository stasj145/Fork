/**
 * Activity API types
 * These types match the backend schemas for activity endpoints
 */

// ============================================================================
// SHARED TYPES
// ============================================================================

export enum ActivitySources {
  LOCAL = 'local',
  PERSONAL = 'personal',
}

export interface ActivityInDB {
  id: string
  user_id: string
  name: string
  calories_burned_kg_h: number
  private: boolean
}

export interface ActivityDetailed extends ActivityInDB {}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface ActivityCreateRequest {
  name: string
  calories_burned_kg_h: number
}

export interface ActivityUpdateRequest {
  name?: string | null
  calories_burned_kg_h?: number | null
  private?: boolean | null
}

export interface ActivitySearchRequest {
  query?: string | null
  limit?: number | null
  source?: ActivitySources | null
}

// ============================================================================
// CONSTRUCTORS
// ============================================================================

export const createEmptyActivity = (): ActivityInDB => ({
  id: '',
  user_id: '',
  name: '',
  calories_burned_kg_h: 0.0,
  private: false,
})
