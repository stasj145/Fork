import type { Goals } from './user'
import type { Activity } from './activity'

export interface ActivityLog {
  id?: string
  date: string
  activity_entries: ActivityEntry[]
  goals: Goals
}

export interface ActivityEntry {
  id?: string
  activity: Activity
  duration: number
  calories_burned: number
}
