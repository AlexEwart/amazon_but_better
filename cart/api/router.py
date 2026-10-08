import logging

from fastapi import APIRouter, FastAPI, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dummy Cart Service")
cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.get("/{user_id}")
async def get_cart(user_id: str):
    logger.info("Dummy Cart: GET /cart/%s", user_id)
    return {"user_id": user_id, "items": ["product-101", "product-202"]}


@cart_router.post("/{user_id}")
async def add_to_cart(user_id: str, product_id: str = Query(...)):
    logger.info("Dummy Cart: POST /cart/%s?product_id=%s", user_id, product_id)
    return {"user_id": user_id, "items": ["product-101", "product-202", product_id]}


@cart_router.delete("/{user_id}")
async def clear_cart(user_id: str):
    logger.info("Dummy Cart: DELETE /cart/%s", user_id)
    return {"user_id": user_id, "items": [], "message": "Cart cleared (stub)"}


app.include_router(cart_router)
