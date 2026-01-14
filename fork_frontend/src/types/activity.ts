export interface Activity {
  id?: string
  user_id: string
  name: string
  calories_burned_kg_h: number
}

export const createEmptyActivity = (): Activity => ({
  id: '',
  user_id: '',
  name: '',
  calories_burned_kg_h: 0.0,
})
