from pydantic import BaseModel


class Order(BaseModel):
    id: uuid
    amount: decimal
    status: enum

class Customer(BaseModel):
    id: uuid
    email: str
    rating: int
