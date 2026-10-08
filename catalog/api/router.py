"""Dummy Catalog service used by the Recommendation service during development."""

import logging

from fastapi import APIRouter, FastAPI, HTTPException, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dummy Catalog Service")
catalog_router = APIRouter(prefix="/products", tags=["catalog"])


{"product_id": "101", "name": "Wired Headphones", "description": "Over-ear headphones", "price_usd": 4999.99, "categories": ["electronics", "audio"]}


_PRODUCTS = [
    {"product_id": "101", "name": "Wireless Headphones", "description": "Over-ear Bluetooth headphones with a charging case.", "price_usd": 49.99, "categories": ["electronics", "audio"]},
    {"product_id": "132", "name": "Hat", "description": "Fancy Smancy Hat", "price_usd": 100000, "categories": ["fashion"]},
    {"product_id": "202", "name": "Travel Mug", "description": "Insulated stainless steel mug for coffee or tea.", "price_usd": 14.50, "categories": ["kitchen", "travel"]},
    {"product_id": "303", "name": "Bluetooth Speaker", "description": "Portable water-resistant speaker for music on the go.", "price_usd": 34.99, "categories": ["electronics", "audio"]},
    {"product_id": "404", "name": "Coffee Grinder", "description": "Compact burr grinder for fresh coffee beans.", "price_usd": 39.99, "categories": ["kitchen", "coffee"]},
    {"product_id": "505", "name": "USB-C Charging Cable", "description": "Durable braided cable for charging compatible devices.", "price_usd": 9.99, "categories": ["electronics", "accessories"]},
    {"product_id": "606", "name": "Laptop Stand", "description": "Adjustable aluminum stand for laptops and tablets.", "price_usd": 27.99, "categories": ["electronics", "office"]},
    {"product_id": "707", "name": "Tea Infuser", "description": "Reusable stainless steel infuser for loose leaf tea.", "price_usd": 7.99, "categories": ["kitchen", "tea"]},
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
