"""Recommendation logic and HTTP clients for the Cart and Catalog services."""

import logging
import os
from collections.abc import Callable
from typing import Any

import httpx

from .models import Product

logger = logging.getLogger(__name__)


class RecommendationService:
    """Finds non-cart products that share categories with a user's cart."""

    def __init__(
        self,
        cart_url: str | None = None,
        catalog_url: str | None = None,
        client_factory: Callable[[], httpx.AsyncClient] = httpx.AsyncClient,
    ):
        self.cart_url = cart_url or os.getenv("CART_SERVICE_URL", "http://localhost:8001")
        self.catalog_url = catalog_url or os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")
        self.client_factory = client_factory

    async def get_recommendations(
        self,
        user_id: str,
        correlation_id: str | None = None,
        request_context: dict[str, Any] | None = None,
    ) -> list[Product]:
        """Return up to five non-cart products with a matching cart category."""
        headers = {"correlation-id": correlation_id} if correlation_id else {}
        async with self.client_factory() as client:
            cart_response = await client.get(f"{self.cart_url}/cart/{user_id}", headers=headers)
            cart_response.raise_for_status()
            cart_data = cart_response.json()
            if request_context is not None:
                request_context["cart"] = cart_data.get("cart", []) if isinstance(cart_data, dict) else cart_data
            catalog_response = await client.get(f"{self.catalog_url}/products", headers=headers)
            catalog_response.raise_for_status()

        cart_items = cart_data.get("cart") or [] if isinstance(cart_data, dict) else cart_data or []
        cart_product_ids = {item["product_id"] for item in cart_items}
        products = [Product.model_validate(product) for product in catalog_response.json()]
        cart_categories = {
            category
            for product in products
            if product.product_id in cart_product_ids
            for category in product.categories
        }

        candidates = [
            product
            for product in products
            if product.product_id not in cart_product_ids
            and cart_categories.intersection(product.categories)
        ]
        ranked = sorted(
            candidates,
            key=lambda product: (len(cart_categories.intersection(product.categories)), product.name),
            reverse=True,
        )
        recommendations = ranked[:5]

        logger.info("Created %d recommendations for user %s", len(recommendations), user_id)
        return recommendations
