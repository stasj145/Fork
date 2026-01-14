# Fork

Fork is a nutrition tracking system with a focus on self hosting, where your health data never leaves your control. It's built in Python + FastAPI for the backend and Vue 3 for the frontend.

Features include, but are not limited to:
- Tracking of calorie and macronutrient intake
- Tracking of burned calories through activities
- Access to a fully local food database, right on your server. Additionally, OpenFoodFacts integration can be used to access over 3.5 million products from around the world.
- Local vector-embedding-based search for your food. Based on pgvector and intfloat/multilingual-e5-small. Very fast, even on CPU.
- Barcode scanning for quick and easy access to both your local and OpenFoodFacts foods.
- Recipes: Easily create combined food items to track your common recipes.
- Easily install Fork on any mobile device as a Progressive Web App or simply use it in the browser. Access it with any device you want!


## Docker Setup

This project includes Docker configuration for easy deployment. The setup consists of:

1. A PostgreSQL database with pgvector extension
2. The FastAPI backend application
3. The Vue3 frontend served with nginx

### Running with Docker

Customize the docker compose and/or .env file and run the compose file.

   ```bash
   docker-compose up
   ```

The website will be available at `http://localhost:8080`

NOTE: On first startup the food and activities are imported. This may take a couple of minutes. However, the website should already be up and accesable during this time.


### Acknowledgment
- The following dataset was used for activity information: https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities
- The OpenNutrition dataset was used for generic food data: https://www.opennutrition.app/
- OpenFoodFacts is used for online food resources i.e. for barcode scanning: https://world.openfoodfacts.org/