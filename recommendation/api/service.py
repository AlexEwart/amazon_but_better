"""Recommendation logic and HTTP clients for the Cart and Catalog services."""

import logging
import os
from collections.abc import Callable

import httpx

from .models import Product

logger = logging.getLogger(__name__)


class RecommendationService:
    """Ranks non-cart products by the categories represented in a user's cart."""

    def __init__(
        self,
        cart_url: str | None = None,
        catalog_url: str | None = None,
        client_factory: Callable[[], httpx.AsyncClient] = httpx.AsyncClient,
    ):
        self.cart_url = cart_url or os.getenv("CART_SERVICE_URL", "http://localhost:8001")
        self.catalog_url = catalog_url or os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")
        self.client_factory = client_factory

    async def get_recommendations(self, user_id: str) -> list[Product]:
        """Return up to five non-cart products ranked by shared cart categories."""
        async with self.client_factory() as client:
            cart_response = await client.get(f"{self.cart_url}/cart/{user_id}")
            cart_response.raise_for_status()
            catalog_response = await client.get(f"{self.catalog_url}/products")
            catalog_response.raise_for_status()

        cart_product_ids = set(cart_response.json().get("items", []))
        products = [Product.model_validate(product) for product in catalog_response.json()]
        cart_categories = {
            category
            for product in products
            if product.product_id in cart_product_ids
            for category in product.categories
        }

        candidates = [product for product in products if product.product_id not in cart_product_ids]
        ranked = sorted(
            candidates,
            key=lambda product: (len(cart_categories.intersection(product.categories)), product.name),
            reverse=True,
        )
        recommendations = ranked[:5]

        logger.info("Created %d recommendations for user %s", len(recommendations), user_id)
        return recommendations
