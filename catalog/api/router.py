"""Dummy Catalog service used by the Recommendation service during development."""

import logging
import asyncio
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request

from request_logging import log_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dummy Catalog Service")
catalog_router = APIRouter(prefix="/products", tags=["catalog"])


@app.middleware("http")
async def log_catalog_request(request: Request, call_next):
    incoming_id = request.headers.get("correlation_id", "")
    try:
        correlation_id = str(UUID(incoming_id))
    except ValueError:
        correlation_id = str(uuid4())

    response = await call_next(request)
    response.headers["correlation_id"] = correlation_id
    await asyncio.to_thread(
        log_request,
        user_id=None,
        cart=None,
        endpoint=request.url.path,
        method=request.method,
        correlation_id=correlation_id,
    )
    return response




_PRODUCTS = [
    {"product_id": "101", "name": "Wireless Headphones", "description": "Over-ear Bluetooth headphones with a charging case.", "price": 49.99, "categories": ["electronics", "audio"]},
    {"product_id": "102", "name": "Wired Headphones", "description": "Over-ear headphones", "price": 4999.99, "categories": ["electronics", "audio"]},
    {"product_id": "132", "name": "Hat", "description": "Fancy Smancy Hat", "price": 100000, "categories": ["fashion"]},
    {"product_id": "202", "name": "Travel Mug", "description": "Insulated stainless steel mug for coffee or tea.", "price": 14.50, "categories": ["kitchen", "travel"]},
    {"product_id": "303", "name": "Bluetooth Speaker", "description": "Portable water-resistant speaker for music on the go.", "price": 34.99, "categories": ["electronics", "audio"]},
    {"product_id": "404", "name": "Coffee Grinder", "description": "Compact burr grinder for fresh coffee beans.", "price": 39.99, "categories": ["kitchen", "coffee"]},
    {"product_id": "505", "name": "USB-C Charging Cable", "description": "Durable braided cable for charging compatible devices.", "price": 9.99, "categories": ["electronics", "accessories"]},
    {"product_id": "606", "name": "Laptop Stand", "description": "Adjustable aluminum stand for laptops and tablets.", "price": 27.99, "categories": ["electronics", "office"]},
    {"product_id": "707", "name": "Tea Infuser", "description": "Reusable stainless steel infuser for loose leaf tea.", "price": 7.99, "categories": ["kitchen", "tea"]},
]


@catalog_router.get("")
@catalog_router.get("/")
async def get_products(search_string: str | None = Query(default=None)):
    logger.info("Dummy Catalog: GET /products?search_string=%s", search_string)
    if not search_string:
        return _PRODUCTS
    search = search_string.lower()
    return [product for product in _PRODUCTS if search in product["name"].lower() or search in product["description"].lower()]


@catalog_router.get("/{product_id}")
async def get_product(product_id: str):
    logger.info("Dummy Catalog: GET /products/%s", product_id)
    for product in _PRODUCTS:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


app.include_router(catalog_router)
