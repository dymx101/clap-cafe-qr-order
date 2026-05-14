# backend/tests/core/test_order_service.py
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.order_service import (
    InvalidStatusTransitionError,
    ItemOutOfStockError,
    OrderNotFoundError,
    OrderService,
    SeatNotVacantError,
    _options_key,
)
from app.models import (
    Category,
    Item,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    Seat,
)


class TestOrderDedupKey:
    def test_options_key_deterministic(self):
        items = [{"item_id": "abc", "quantity": 1, "options": {"size": "M"}}]
        key1 = _options_key("T01", items)
        key2 = _options_key("T01", items)
        assert key1 == key2

    def test_options_key_diff_seat(self):
        items = [{"item_id": "abc", "quantity": 1, "options": {}}]
        key1 = _options_key("T01", items)
        key2 = _options_key("T02", items)
        assert key1 != key2

    def test_options_key_diff_items(self):
        key1 = _options_key("T01", [{"item_id": "a", "quantity": 1, "options": {}}])
        key2 = _options_key("T01", [{"item_id": "b", "quantity": 1, "options": {}}])
        assert key1 != key2


class TestOrderStatusTransitions:
    def test_valid_transitions(self):
        from app.models import ORDER_STATUS_TRANSITIONS, OrderStatus

        # submitted can go to confirmed, rejected, cancelled
        assert OrderStatus.CONFIRMED in ORDER_STATUS_TRANSITIONS[OrderStatus.SUBMITTED]
        assert OrderStatus.REJECTED in ORDER_STATUS_TRANSITIONS[OrderStatus.SUBMITTED]
        assert OrderStatus.CANCELLED in ORDER_STATUS_TRANSITIONS[OrderStatus.SUBMITTED]

    def test_preparing_valid_targets(self):
        from app.models import ORDER_STATUS_TRANSITIONS, OrderStatus

        assert OrderStatus.READY in ORDER_STATUS_TRANSITIONS[OrderStatus.PREPARING]
        assert OrderStatus.CANCELLED in ORDER_STATUS_TRANSITIONS[OrderStatus.PREPARING]

    def test_completed_has_no_transitions(self):
        from app.models import ORDER_STATUS_TRANSITIONS, OrderStatus

        assert len(ORDER_STATUS_TRANSITIONS[OrderStatus.COMPLETED]) == 0


class TestOrderServiceValidation:
    def test_invalid_order_id_format(self):
        import re

        assert re.match(r"^CC-\d{8}-\d{3}$", "CC-20260514-001")
        assert re.match(r"^CC-\d{8}-\d{3}$", "CC-20260514-999")
        assert not re.match(r"^CC-\d{8}-\d{3}$", "CC-20260514-01")  # too few digits
        assert not re.match(r"^CC-\d{8}-\d{3}$", "invalid")
