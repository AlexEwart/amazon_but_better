import logging
import asyncio
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Request

from .models import Product
from .service import RecommendationService
from request_logging import log_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recommendation Service")
recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])
rec_service = RecommendationService()


@app.middleware("http")
async def log_recommendation_request(request: Request, call_next):
    incoming_id = request.headers.get("correlation-id", "")
    try:
        correlation_id = str(UUID(incoming_id))
    except ValueError:
        correlation_id = str(uuid4())

    request.state.correlation_id = correlation_id
    request.state.user_id = None
    request.state.cart = None
    response = await call_next(request)
    response.headers["correlation-id"] = correlation_id
    await asyncio.to_thread(
        log_request,
        user_id=request.state.user_id,
        cart=request.state.cart,
        endpoint=request.url.path,
        method=request.method,
        correlation_id=correlation_id,
    )
    return response


@app.get("/")
async def read_root():
    return {"service": "recommendation", "status": "ok"}


@recommendation_router.get("/{user_id}", response_model=list[Product])
async def get_recommendations(user_id: str, request: Request):
    request.state.user_id = user_id
    request_context = {}
    try:
        return await rec_service.get_recommendations(
            user_id,
            correlation_id=request.state.correlation_id,
            request_context=request_context,
        )
    except httpx.HTTPError as exc:
        logger.exception("Could not retrieve dependency data")
        raise HTTPException(status_code=502, detail="Cart or Catalog service is unavailable") from exc
    finally:
        request.state.cart = request_context.get("cart")


app.include_router(recommendation_router)


