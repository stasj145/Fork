import { useAuthStore } from '@/stores/auth'

export const fetchWrapper = {
  get: request('GET'),
  post: request('POST'),
  put: request('PUT'),
  delete: request('DELETE'),
  patch: request('PATCH'),
}

function request(method: string) {
  return (url: string, body?: string | object | FormData): Promise<any> => {

    const headers: Record<string, string> = {
      ...authHeader(url), // Spread the auth header
    }

    const requestOptions: RequestInit = {
      method,
      headers,
    }

    if (body) {
      if (body instanceof FormData) {
        // Handle FormData (e.g., file uploads)
        requestOptions.body = body
      } else if (body instanceof URLSearchParams) {
        // For form data (login)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        requestOptions.body = body.toString()
      } else {
        // For JSON data (most other requests)
        headers['Content-Type'] = 'application/json'
        requestOptions.body = JSON.stringify(body)
      }
    }

    return fetch(url, requestOptions as any).then(handleResponse)
  }
}

// helper functions
function authHeader(url: string): Record<string, string> {
  // return auth header with jwt if user is logged in and request is to the api url
  const store = useAuthStore()
  const isLoggedIn = !!store.user?.access_token
  const isApiUrl = url.startsWith('/api') || url.startsWith(import.meta.env.VITE_API_URL as string)
  if (isLoggedIn && isApiUrl && store.user) {
    return { Authorization: `Bearer ${store.user.access_token}` }
  } else {
    return {}
  }
}

async function handleResponse(response: Response): Promise<any> {
  const contentType = response.headers.get('content-type') || ''

  if (!response.ok) {
    const isJson = contentType.includes('application/json')
    const data = isJson ? await response.json() : null

    const store = useAuthStore()
    if ([401, 403].includes(response.status) && store.user) {
      store.logout()
    }
    const errorMsg = (data && data.detail) || response.statusText
    return Promise.reject(new Error(errorMsg))
  }

  if (contentType.includes('application/json')) {
    return await response.json()
  }

  if (contentType.includes('image/') || contentType.includes('application/octet-stream')) {
    return await response.arrayBuffer()
  }

  return await response.text()
}
