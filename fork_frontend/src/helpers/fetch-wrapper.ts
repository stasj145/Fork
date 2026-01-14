import { useAuthStore } from '@/stores/auth'

interface FetchOptions {
  method: string
  headers: Record<string, string>
  body?: string
}

export const fetchWrapper = {
  get: request('GET'),
  post: request('POST'),
  put: request('PUT'),
  delete: request('DELETE'),
  patch: request('PATCH'),
}

function request(method: string) {
  return (url: string, body?: any): Promise<any> => {
    const requestOptions: FetchOptions = {
      method,
      headers: authHeader(url),
    }

    if (body) {
      if (body instanceof URLSearchParams) {
        // For form data (login)
        requestOptions.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        requestOptions.body = body.toString()
      } else {
        // For JSON data (most other requests)
        requestOptions.headers['Content-Type'] = 'application/json'
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
  const isJson = response.headers?.get('content-type')?.includes('application/json')
  const data = isJson ? await response.json() : null

  if (!response.ok) {
    const store = useAuthStore()
    if ([401, 403].includes(response.status) && store.user) {
      // auto logout if 401 Unauthorized or 403 Forbidden response returned from api
      store.logout()
    }

    // get error message from body or default to response status
    const errorMsg = (data && data.detail) || response.statusText
    return Promise.reject(new Error(errorMsg))
  }

  return data
}
