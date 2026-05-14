# backend/app/schemas/payment.py
from typing import List, Optional

from pydantic import BaseModel


class PaymentIntentCreate(BaseModel):
    order_id: str
    payment_method_types: List[str] = ["card"]


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: int  # cents
    currency: str = "sgd"


class PayNowConfirmRequest(BaseModel):
    order_id: str
    payment_method_type: str = "paynow"


class PayNowConfirmResponse(BaseModel):
    paynow_qr_url: str
    paynow_reference: str
    expires_at: str


class PaymentStatusResponse(BaseModel):
    status: str  # pending/processing/succeeded/failed
