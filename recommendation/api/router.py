import logging

import httpx
from fastapi import APIRouter, FastAPI, HTTPException

from .models import Product
from .service import RecommendationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recommendation Service")
recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])
rec_service = RecommendationService()


@app.get("/")
async def read_root():
    return {"service": "recommendation", "status": "ok"}


@recommendation_router.get("/{user_id}", response_model=list[Product])
async def get_recommendations(user_id: str):
    try:
        return await rec_service.get_recommendations(user_id)
    except httpx.HTTPError as exc:
        logger.exception("Could not retrieve dependency data")
        raise HTTPException(status_code=502, detail="Cart or Catalog service is unavailable") from exc


app.include_router(recommendation_router)


