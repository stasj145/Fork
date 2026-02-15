![logo](https://github.com/stasj145/Fork/blob/main/fork_frontend/public/pwa-192x192.png)

# Fork

Fork is a nutrition tracking system with a focus on self hosting, where your health data never leaves your control. It's built in Python + FastAPI for the backend and Vue 3 for the frontend.

Features include, but are not limited to:
- Tracking of calorie and macronutrient intake
- Tracking of burned calories through activities
- Gain valuable insights about your progress towards your goals through detailed graphs and KPIs.
- Recipes: Easily create combined food items to track your common recipes.
- OpenFoodFacts integration can be used to access over 3.5 million products from around the world.
- Integration with Tandoor Recipes (https://github.com/TandoorRecipes/recipes) for easy tracking of your own recipes
- Barcode scanning for quick and easy access to both your local and OpenFoodFacts foods.
- Access to a fully local food database, right on your server. (Based on the OpenNutrition Foods Dataset)
- Local vector-embedding-based search for your food. Based on pgvector and intfloat/multilingual-e5-small. Very fast, even on CPU.
- Easily install Fork on any mobile device as a Progressive Web App (PWA) or simply use it in the browser. Access it with any device you want!

## Example Images
<img height="1300" alt="grafik" src="https://github.com/user-attachments/assets/cdef1101-2e75-4fb7-a923-290e94839cd1" />
<img height="1000" alt="firefox_9I6CvTcY8F" src="https://github.com/user-attachments/assets/c840de13-f8bb-4672-b58f-9653c7e39e55" />
<img height="600" alt="firefox_r9rzbk6mgy" src="https://github.com/user-attachments/assets/d4b6d28c-1c31-4a19-b3ad-88ec6de33343" />
<img height="600" alt="firefox_g8C05dPl6N" src="https://github.com/user-attachments/assets/e73ef3c9-d104-4613-ac6e-be087af074bd" />


## Docker Setup

This project includes Docker configuration for easy deployment. The setup consists of:

1. A PostgreSQL database with pgvector extension
2. The FastAPI backend application served with uvicorn
3. The Vue3 frontend served with nginx

### Running with Docker

Customize the docker compose and/or .env file and run the compose file.

   ```bash
   docker-compose up
   ```

The website will be available at `http://localhost:8080`.

For any production environment, it's strongly recommended to use a reverse proxy (like Nginx Proxy Manager, Traefik, Caddy, ...) to access Fork instead of accessing directly at http://localhost:8080.

NOTE: On first startup the food and activities are imported and vector embeddings created. This may take a couple of minutes. However, the website should already be up and accesable during this time as this happens asynchronously.

### Acknowledgment
- The following dataset was used for activity information: https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities
- The OpenNutrition dataset was used for generic food data: https://www.opennutrition.app/
- OpenFoodFacts is used for online food resources i.e. for barcode scanning: https://world.openfoodfacts.org/
