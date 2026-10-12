from pydantic import BaseModel


class Product(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    categories: list[str]

