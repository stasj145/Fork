import type { Goals } from './user'
import type { Food } from './food'

export interface FoodLog {
  id?: string
  date: string
  notes?: string
  food_entries: FoodEntry[]
  goals: Goals
}

export interface FoodEntry {
  id?: string
  food_item: Food
  meal_type: string
  quantity: number
}
