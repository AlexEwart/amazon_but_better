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


## Submit the Cloud Build pipeline

From any directory inside this Git repository, first change to the repository root and define the build variables:

```bash
cd "$(git rev-parse --show-toplevel)"

export REPOSITORY=ewart-microservices-repo
export PROJECTID=ewart-microservices
export REGION=us-central1
export BUCKET=ewart-microservices_cloudbuild
export TAG="$(git rev-parse --short HEAD)"
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/ewart-service-account-key.json"
```

`$PWD` makes the key path absolute. This works whether the command was started from the repository root or from `recommendation/`.

```bash
gcloud auth activate-service-account \
  --key-file="$GOOGLE_APPLICATION_CREDENTIALS" \
  --project="$PROJECTID"

gcloud builds submit \
  --region="$REGION" \
  --config=cloudbuild.yaml \
  --substitutions=_ARTIFACT_REGISTRY_REPO="$REPOSITORY",_BUCKET_NAME="$BUCKET",SHORT_SHA="$TAG" \
  .

gcloud run deploy cart \
  --image "$REGION-docker.pkg.dev/$PROJECTID/$REPOSITORY/cart:$TAG" \
  --region "$REGION" \
  --port 8001 \
  --allow-unauthenticated

gcloud run deploy catalog \
  --image "$REGION-docker.pkg.dev/$PROJECTID/$REPOSITORY/catalog:$TAG" \
  --region "$REGION" \
  --port 8002 \
  --allow-unauthenticated

export CART_URL="$(gcloud run services describe cart --region="$REGION" --format='value(status.url)')"
export CATALOG_URL="$(gcloud run services describe catalog --region="$REGION" --format='value(status.url)')"

export CART_URL=http://34.121.75.149:8080



gcloud run deploy recommendation \
  --image "$REGION-docker.pkg.dev/$PROJECTID/$REPOSITORY/recommendation:$TAG" \
  --region "$REGION" \
  --port 8000 \
  --allow-unauthenticated \
  --set-env-vars CART_SERVICE_URL="$CART_URL",CATALOG_SERVICE_URL="$CATALOG_URL"

```
