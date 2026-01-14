# Fork Backend

Backend of Fork built with Python + FastAPI.

## Docker Setup

This project includes Docker configuration for easy deployment. The setup consists of:

1. A PostgreSQL database with pgvector extension
2. The FastAPI backend application

### Environment Variables

The following environment variables can be configured:

- `FORK_BACKEND_ADMIN_USERNAME`=admin
- `FORK_BACKEND_ADMIN_EMAIL`=fork-admin@example.com
- `FORK_BACKEND_ADMIN_PASSWORD`=admin
- `FORK_BACKEND_SECRET_KEY`=very_secret_key_here_change_this_in_production
- `FORK_POSTGRES_USER`=fork_user
- `FORK_POSTGRES_PASSWORD`=fork_password
- `FORK_POSTGRES_DB_NAME`=fork_db
- `FORK_POSTGRES_URL`=fork_postgres

### Running with Docker

Run the backend:
   ```bash
   docker-compose up
   ```

The api will be available at `http://localhost:8000`

### Development

For development, you can also run the application directly:
```bash
# Install dependencies
pip install .

# Run the application
uvicorn main:uvicorn_entry --host 0.0.0.0 --port 8000 --factory --reload
```

### Acknowledgment
- The following dataset was used for activity information: https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities
- The OpenNutrition dataset was used for generic food data: https://www.opennutrition.app/
- OpenFoodFacts is used for online food resources i.e. for barcode scanning: https://world.openfoodfacts.org/