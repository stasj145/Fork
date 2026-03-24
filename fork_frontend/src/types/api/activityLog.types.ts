/**
 * Activity Log API types
 * These types match the backend schemas for activity log endpoints
 */

import type { ActivityInDB } from './activity.types'
import type { GoalsBase } from './user.types'

// ============================================================================
// SHARED TYPES
// ============================================================================

export interface ActivityEntryInDB {
  id: string
  activity: ActivityInDB
  duration: number
  calories_burned: number | null
}

export interface ActivityLogInDB {
  id: string
  date: string
  activity_entries: ActivityEntryInDB[]
  goals: GoalsBase
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface ActivityEntryCreateRequest {
  activity_id: string
  duration: number
  calories_burned?: number | null
}

export interface ActivityEntryUpdateRequest {
  duration?: number | null
  calories_burned?: number | null
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export type ActivityLogInDBResponse = ActivityLogInDB

export type ActivityEntryInDBResponse = ActivityEntryInDB