export interface Ingredient {
  parent_id: string | null
  ingredient_id: string
  quantity: number
  ingredient: Food
}

export interface Food {
  id?: string
  name: string
  brand: string
  barcode: string | null
  private: boolean
  hidden: boolean
  description: string
  serving_size: number
  serving_unit: string
  calories_per_100: number
  protein_per_100: number
  carbs_per_100: number
  fat_per_100: number
  calories_per_serving?: number
  protein_per_serving?: number
  carbs_per_serving?: number
  fat_per_serving?: number

  ingredients: Ingredient[]
}

export const createEmptyFood = (): Food => ({
  name: '',
  brand: 'Generic',
  private: true,
  hidden: false,
  barcode: null,
  description: '',
  serving_size: 1.0,
  serving_unit: 'serving',
  calories_per_100: 0.0,
  protein_per_100: 0.0,
  carbs_per_100: 0.0,
  fat_per_100: 0.0,
  calories_per_serving: 0.0,
  protein_per_serving: 0.0,
  carbs_per_serving: 0.0,
  fat_per_serving: 0.0,
  ingredients: [],
})

export const createEmptyIngredient = (): Ingredient => ({
  parent_id: null,
  ingredient_id: 'Generic',
  quantity: 1.0,
  ingredient: createEmptyFood(),
})
