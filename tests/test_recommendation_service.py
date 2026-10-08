import httpx
import pytest

from recommendation.api.service import RecommendationService


@pytest.mark.asyncio
async def test_recommendations_exclude_cart_items_and_rank_shared_categories():
    products = [
        {"product_id": "product-101", "name": "Wireless Headphones", "description": "Headphones", "price_usd": 49.99, "categories": ["electronics", "audio"]},
        {"product_id": "product-202", "name": "Travel Mug", "description": "Mug", "price_usd": 14.50, "categories": ["kitchen", "travel"]},
        {"product_id": "product-303", "name": "Bluetooth Speaker", "description": "Speaker", "price_usd": 34.99, "categories": ["electronics", "audio"]},
        {"product_id": "product-404", "name": "Coffee Grinder", "description": "Grinder", "price_usd": 39.99, "categories": ["kitchen", "coffee"]},
    ]
    cart = {"user_id": "student", "cart": [products[0], products[1]]}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cart/student":
            return httpx.Response(200, json=cart)
        if request.url.path == "/products":
            return httpx.Response(200, json=products)
        return httpx.Response(404)

    service = RecommendationService(
        cart_url="http://cart.test",
        catalog_url="http://catalog.test",
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    recommendations = await service.get_recommendations("student")

    assert [item.product_id for item in recommendations] == ["product-303", "product-404"]
    assert all(item.product_id not in {"product-101", "product-202"} for item in recommendations)


@pytest.mark.asyncio
async def test_recommendations_return_no_more_than_five_products():
    products = [
        {"product_id": "cart-product", "name": "Cart Product", "description": "Cart item", "price_usd": 10.0, "categories": ["electronics"]},
        *[
            {"product_id": f"product-{number}", "name": f"Product {number}", "description": "Catalog item", "price_usd": 10.0, "categories": ["electronics"]}
            for number in range(8)
        ],
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cart/student":
            return httpx.Response(200, json={"cart": [products[0]]})
        if request.url.path == "/products":
            return httpx.Response(200, json=products)
        return httpx.Response(404)

    service = RecommendationService(
        cart_url="http://cart.test",
        catalog_url="http://catalog.test",
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    assert len(await service.get_recommendations("student")) == 5


@pytest.mark.asyncio
async def test_recommendations_exclude_products_without_a_matching_category():
    products = [
        {"product_id": "cart-product", "name": "Headphones", "description": "Cart item", "price_usd": 50.0, "categories": ["electronics"]},
        {"product_id": "matching-product", "name": "Cable", "description": "Matches", "price_usd": 10.0, "categories": ["electronics", "accessories"]},
        {"product_id": "unrelated-product", "name": "Mug", "description": "Does not match", "price_usd": 12.0, "categories": ["kitchen"]},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cart/student":
            return httpx.Response(200, json={"cart": [products[0]]})
        if request.url.path == "/products":
            return httpx.Response(200, json=products)
        return httpx.Response(404)

    service = RecommendationService(
        cart_url="http://cart.test",
        catalog_url="http://catalog.test",
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    recommendations = await service.get_recommendations("student")

    assert [product.product_id for product in recommendations] == ["matching-product"]


@pytest.mark.asyncio
async def test_empty_cart_field_returns_no_recommendations():
    products = [
        {"product_id": "product-1", "name": "Speaker", "description": "Catalog item", "price_usd": 10.0, "categories": ["electronics"]},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cart/student":
            return httpx.Response(200, json={"user_id": "student", "cart": None})
        if request.url.path == "/products":
            return httpx.Response(200, json=products)
        return httpx.Response(404)

    service = RecommendationService(
        cart_url="http://cart.test",
        catalog_url="http://catalog.test",
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    assert await service.get_recommendations("student") == []


@pytest.mark.asyncio
async def test_recommendations_accept_cart_items_as_product_objects():
    products = [
        {"product_id": "101", "name": "Wireless Headphones", "description": "Catalog item", "price_usd": 50.0, "categories": ["electronics", "audio"]},
        {"product_id": "102", "name": "Wired Headphones", "description": "Cart item", "price_usd": 40.0, "categories": ["electronics", "audio"]},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cart/1234":
            return httpx.Response(200, json={"user_id": "1234", "cart": [products[1]]})
        if request.url.path == "/products":
            return httpx.Response(200, json=products)
        return httpx.Response(404)

    service = RecommendationService(
        cart_url="http://cart.test",
        catalog_url="http://catalog.test",
        client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    recommendations = await service.get_recommendations("1234")

    assert [product.product_id for product in recommendations] == ["101"]
