/**
 * Authentication API types
 * These types match the backend schemas for auth endpoints
 */

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface LoginRequest {
  grant_type?: string
  username: string
  password: string
  scope?: string
  client_id?: string
  client_secret?: string
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================


export interface TokenResponse {
  access_token: string
  token_type: string
}
