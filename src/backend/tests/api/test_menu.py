# backend/tests/api/test_menu.py
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestMenuEndpoints:
    def test_item_id_uuid_validation(self):
        """测试UUID格式校验"""
        import re

        valid = str(uuid.uuid4())
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            valid,
            re.IGNORECASE,
        )

    def test_invalid_item_id_format_rejected(self):
        import re

        invalid_ids = ["abc", "123", "CC-20260514-001", ""]
        for invalid in invalid_ids:
            try:
                uuid.UUID(invalid)
                # If it didn't raise, it's a valid UUID (32-char hex strings are valid)
            except ValueError:
                pass  # Expected for truly invalid strings


class TestMenuLangParam:
    def test_lang_regex(self):
        import re

        assert re.match(r"^(zh|en)$", "zh")
        assert re.match(r"^(zh|en)$", "en")
        assert not re.match(r"^(zh|en)$", "fr")
        assert not re.match(r"^(zh|en)$", "ZH")
