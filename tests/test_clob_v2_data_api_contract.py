from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
FETCH_SCRIPT = ROOT / "skill" / "polymarket-account-review-skill" / "scripts" / "fetch_polymarket_summary.py"


def load_fetch_module():
    spec = importlib.util.spec_from_file_location("fetch_polymarket_summary_under_test", FETCH_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class DataApiContractTests(unittest.TestCase):
    def setUp(self):
        self.fetch = load_fetch_module()

    def test_request_json_targets_public_data_api(self):
        seen_urls: list[str] = []

        def fake_urlopen(req, timeout):
            seen_urls.append(req.full_url)
            return FakeResponse(json.dumps([{"value": 12.5}]).encode("utf-8"))

        with patch.object(self.fetch.urllib.request, "urlopen", side_effect=fake_urlopen):
            payload = self.fetch.request_json(
                "/value",
                {"user": "0x56687bf447db6ffa42ffe2204a05edaa20f55839"},
                self.fetch.FetchConfig(timeout_seconds=1, max_retries=0),
            )

        self.assertEqual(payload, [{"value": 12.5}])
        self.assertEqual(len(seen_urls), 1)
        self.assertTrue(seen_urls[0].startswith("https://data-api.polymarket.com/value?"))
        self.assertIn("user=0x56687bf447db6ffa42ffe2204a05edaa20f55839", seen_urls[0])

    def test_paginated_fetch_uses_documented_limit_and_offset(self):
        seen_urls: list[str] = []
        pages = [
            [{"realizedPnl": 1, "timestamp": 1}, {"realizedPnl": 2, "timestamp": 2}],
            [{"realizedPnl": 3, "timestamp": 3}],
        ]

        def fake_urlopen(req, timeout):
            seen_urls.append(req.full_url)
            page = pages.pop(0)
            return FakeResponse(json.dumps(page).encode("utf-8"))

        with patch.object(self.fetch.urllib.request, "urlopen", side_effect=fake_urlopen):
            rows = self.fetch.fetch_paginated(
                "/closed-positions",
                user="0x56687bf447db6ffa42ffe2204a05edaa20f55839",
                page_limit=2,
                max_records=10,
                cfg=self.fetch.FetchConfig(timeout_seconds=1, max_retries=0),
                extra_params={"sortBy": "TIMESTAMP", "sortDirection": "ASC"},
            )

        self.assertEqual([row["realizedPnl"] for row in rows], [1, 2, 3])
        self.assertIn("limit=2", seen_urls[0])
        self.assertIn("offset=0", seen_urls[0])
        self.assertIn("offset=2", seen_urls[1])
        self.assertIn("sortBy=TIMESTAMP", seen_urls[0])

    def test_paginated_fetch_continues_when_api_silently_caps_page_size(self):
        seen_urls: list[str] = []
        pages = [
            [{"realizedPnl": i, "timestamp": i} for i in range(50)],
            [{"realizedPnl": 50 + i, "timestamp": 50 + i} for i in range(12)],
        ]

        def fake_urlopen(req, timeout):
            seen_urls.append(req.full_url)
            page = pages.pop(0) if pages else []
            return FakeResponse(json.dumps(page).encode("utf-8"))

        with patch.object(self.fetch.urllib.request, "urlopen", side_effect=fake_urlopen):
            rows = self.fetch.fetch_paginated(
                "/closed-positions",
                user="0x56687bf447db6ffa42ffe2204a05edaa20f55839",
                page_limit=500,
                max_records=100,
                cfg=self.fetch.FetchConfig(timeout_seconds=1, max_retries=0),
                extra_params={"sortBy": "TIMESTAMP", "sortDirection": "ASC"},
            )

        self.assertEqual(len(rows), 62)
        self.assertIn("limit=500", seen_urls[0])
        self.assertIn("offset=0", seen_urls[0])
        self.assertIn("offset=50", seen_urls[1])

    def test_extract_list_payload_accepts_known_wrappers(self):
        self.assertEqual(self.fetch.extract_list_payload([{"a": 1}]), [{"a": 1}])
        self.assertEqual(self.fetch.extract_list_payload({"value": [{"a": 1}]}), [{"a": 1}])
        self.assertEqual(self.fetch.extract_list_payload({"data": [{"a": 1}]}), [{"a": 1}])
        self.assertEqual(self.fetch.extract_list_payload({"value": "bad"}), [])

    def test_fetcher_retries_429_and_5xx(self):
        attempts = {"count": 0}

        def fake_urlopen(req, timeout):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise urllib.error.HTTPError(req.full_url, 429, "rate limited", hdrs=None, fp=io.BytesIO())
            return FakeResponse(json.dumps({"traded": 7}).encode("utf-8"))

        with patch.object(self.fetch.time, "sleep"), patch.object(self.fetch.urllib.request, "urlopen", side_effect=fake_urlopen):
            payload = self.fetch.request_json(
                "/traded",
                {"user": "0x56687bf447db6ffa42ffe2204a05edaa20f55839"},
                self.fetch.FetchConfig(timeout_seconds=1, max_retries=1),
            )

        self.assertEqual(payload, {"traded": 7})
        self.assertEqual(attempts["count"], 2)

    def test_account_summary_uses_recent_desc_closed_positions_for_7d_30d(self):
        calls: list[dict] = []

        def fake_request_json(path, params, cfg):
            if path == "/value":
                return [{"value": 1}]
            if path == "/traded":
                return {"traded": 2}
            return []

        def fake_request_bytes(path, params, cfg):
            raise RuntimeError("snapshot unavailable")

        def fake_fetch_paginated(path, user, page_limit, max_records, cfg, extra_params=None):
            calls.append({"path": path, "extra_params": extra_params or {}})
            if path != "/closed-positions":
                return []
            direction = (extra_params or {}).get("sortDirection")
            if direction == "ASC":
                return [{"timestamp": 1, "realizedPnl": -10}]
            if direction == "DESC":
                return [{"timestamp": int(self.fetch.time.time()), "realizedPnl": 25}]
            return []

        with (
            patch.object(self.fetch, "request_json", side_effect=fake_request_json),
            patch.object(self.fetch, "request_bytes", side_effect=fake_request_bytes),
            patch.object(self.fetch, "fetch_paginated", side_effect=fake_fetch_paginated),
        ):
            summary = self.fetch.fetch_account_summary(
                account="0x56687bf447db6ffa42ffe2204a05edaa20f55839",
                page_limit=500,
                max_closed_records=5000,
                max_open_records=5000,
                cfg=self.fetch.FetchConfig(timeout_seconds=1, max_retries=0),
            )

        closed_calls = [c for c in calls if c["path"] == "/closed-positions"]
        self.assertEqual(closed_calls[0]["extra_params"]["sortDirection"], "ASC")
        self.assertEqual(closed_calls[1]["extra_params"]["sortDirection"], "DESC")
        self.assertEqual(summary["summary"]["closed_positions_realized_pnl_30d"], 25)
        self.assertEqual(summary["summary"]["closed_positions_realized_pnl_7d"], 25)

    def test_source_tree_has_no_legacy_clob_v1_trading_surface(self):
        excluded_dirs = {".git", ".codex-longrun", "output", "reportcase_26account_full", "tests"}
        checked_suffixes = {".py"}
        forbidden = [
            "py_clob_client",
            "py-clob-client",
            "@polymarket/clob-client",
            "clob.polymarket.com",
            "feeRateBps",
            "create_order",
            "post_order",
        ]

        offenders: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in checked_suffixes:
                continue
            if any(part in excluded_dirs for part in path.relative_to(ROOT).parts):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
