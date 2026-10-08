from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    color: str = "#3b82f6"

class SubscriptionCreate(BaseModel):
    name: str
    amount: float
    interval_type: str # weekly, monthly, yearly
    category_id: int
    start_date: str
    next_due_date: str
    payment_type: str = "Überweisung"

class SubscriptionUpdate(BaseModel):
    name: str
    amount: float
    interval_type: str
    category_id: int
    next_due_date: str
    payment_type: str

class PaymentRecord(BaseModel):
    subscription_id: int
    amount: float
    paid_date: str
    status: str = "paid"
