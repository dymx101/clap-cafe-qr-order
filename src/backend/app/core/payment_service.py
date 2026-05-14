# backend/app/core/payment_service.py
import asyncio
import time

import stripe as stripe_lib
from app.config import settings

stripe_lib.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:

    def create_payment_intent(
        self,
        order_id: str,
        amount_cents: int,
        metadata: dict,
        payment_method_types: list = None,
    ):
        if payment_method_types is None:
            payment_method_types = ["card", "grabpay", "paynow"]
        intent = stripe_lib.PaymentIntent.create(
            amount=amount_cents,
            currency="sgd",
            metadata={**metadata, "order_id": order_id},
            payment_method_types=payment_method_types,
            automatic_payment_methods={"enabled": True},
            expires_at=int(time.time()) + settings.STRIPE_PAYMENT_TIMEOUT_MINUTES * 60,
        )
        return intent

    def construct_webhook_event(self, payload: bytes, signature: str):
        return stripe_lib.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )

    async def construct_webhook_event_async(self, payload: bytes, signature: str):
        return await asyncio.to_thread(
            stripe_lib.Webhook.construct_event,
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    def retrieve_payment_intent(self, intent_id: str):
        return stripe_lib.PaymentIntent.retrieve(intent_id)

    async def retrieve_payment_intent_async(self, intent_id: str):
        return await asyncio.to_thread(stripe_lib.PaymentIntent.retrieve, intent_id)

    def create_refund(self, payment_intent_id: str, amount_cents: int = None):
        kwargs = {"payment_intent": payment_intent_id}
        if amount_cents:
            kwargs["amount"] = amount_cents
        return stripe_lib.Refund.create(**kwargs)
