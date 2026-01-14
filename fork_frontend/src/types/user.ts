export interface User {
  id: string
  username: string
  password?: string
  email: string
  weight: number
  height: number
  age: number
  gender: string
  activity_level: string
  goals: Goals
}

export interface Goals {
  daily_calorie_target: number
  daily_protein_target: number
  daily_carbs_target: number
  daily_fat_target: number
  daily_calorie_burn_target: number
}
