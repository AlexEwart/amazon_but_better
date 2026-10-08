# Amazon But Better services

This repository contains three small FastAPI services for the recommendation-service assignment:

- **Cart** (`/cart/{user_id}`) logs requests and returns canned cart data.
- **Catalog** (`/products` and `/products/{product_id}`) logs requests and returns canned product data.
- **Recommendation** (`/recommendations/{user_id}`) fetches both services over HTTP and ranks products by category overlap with the cart.

The Cart and Catalog services are deliberately dummy implementations: POST and DELETE requests do not persist data.

## Run locally with Docker

```bash
cd amazon_but_better
docker compose up --build
```

Then open `http://localhost:8000/recommendations/demo-user`.

## Run the tests

```bash
cd amazon_but_better
pip install -r requirements.txt
pytest
```

GitHub Actions runs these tests and builds all three Docker images for every push and pull request.

## Deploy to Google Cloud Run

Cloud Run needs each service deployed separately. Deploy Cart and Catalog first, copy their service URLs, then deploy Recommendation with `CART_SERVICE_URL` and `CATALOG_SERVICE_URL` set to those URLs. The user-facing deployment commands are included in the handoff message from Codex.
