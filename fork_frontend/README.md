# Fork Frontend

Frontent of Fork built with Vue.js 3 and TypeScript.

## Development

To run the application in development mode:

```bash
npm run dev
```

Assumes a backend at localhost:8000

## Building for Production

To build the application for production:

```bash
npm run build
```

## Docker

A Dockerfile is provided to containerize the application:

```bash
# Build the Docker image
docker build -t fork-frontend .

# Run the container
docker run -d -p 8080:80 fork-frontend
```

### Docker Configuration

When running in Docker, the application uses nginx to serve the static files. The nginx configuration is set up to serve the frontend and handle client-side routing.

Set "BACKEND_URL" to tell nginx where to find the backend.

### Docker Compose

For a complete setup with backend and database, use the provided docker-compose.yml:

```bash
docker-compose up -d
```

## Proxy Configuration

The development server is configured to proxy API requests to the backend service. The proxy target can be configured using the `VITE_API_PROXY_TARGET` environment variable.

In production, API calls are made directly to the backend service, assuming the frontend and backend are hosted on the same domain or the backend URL is accessible from the client.
