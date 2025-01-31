from pydantic import BaseModel


class Customer(BaseModel):
    name: str
    color: str = '#628594'
