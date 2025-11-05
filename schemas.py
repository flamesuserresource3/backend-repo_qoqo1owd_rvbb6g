"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user"
- Product -> "product"
- ContactMessage -> "contactmessage"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ContactMessage(BaseModel):
    """
    Messages sent from the portfolio contact form.
    Collection name: "contactmessage"
    """
    name: str = Field(..., min_length=2, max_length=100, description="Sender full name")
    email: EmailStr = Field(..., description="Sender email address")
    subject: Optional[str] = Field(None, max_length=150, description="Email subject")
    message: str = Field(..., min_length=10, max_length=5000, description="Message body")


# Example additional schemas you can remove if not needed
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")


class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
