from __future__ import annotations

import importlib.util
import json
import sys
import unittest
import urllib.parse
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PULL_SCRIPT = ROOT / "pull_polymarket_trades_to_csv.py"


def load_pull_module():
    spec = importlib.util.spec_from_file_location("pull_polymarket_trades_to_csv_under_test", PULL_SCRIPT)
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


def _offset(req) -> int:
    parsed = urllib.parse.urlparse(req.full_url)
    query = urllib.parse.parse_qs(parsed.query)
    return int(query["offset"][0])


class ActivityFetchOptimizationTests(unittest.TestCase):
    def setUp(self):
        self.pull = load_pull_module()

    def test_offset_probe_skips_hft_without_requesting_beyond_cap(self):
        calls: list[int] = []

        def fake_urlopen(req, timeout):
            offset = _offset(req)
            calls.append(offset)
            if offset > 3000:
                raise AssertionError("probe optimization should avoid paging beyond the historical cap")
            if offset == 3000:
                return FakeResponse(json.dumps([{"timestamp": 1, "type": "TRADE"}]).encode("utf-8"))
            return FakeResponse(json.dumps([{"timestamp": i, "type": "TRADE"} for i in range(500)]).encode("utf-8"))

        with patch.object(self.pull.urllib.request, "urlopen", side_effect=fake_urlopen):
            with self.assertRaises(self.pull.HighFrequencyAccountError):
                self.pull.fetch_chunk(
                    "0x1111111111111111111111111111111111111111",
                    1000,
                    1000 + 86400,
                    500,
                    1,
                    0,
                    0,
                    0,
                    86400,
                    3000,
                    500,
                )

        self.assertEqual(calls, [0, 3000])

    def test_offset_probe_continues_when_chunk_is_below_cap(self):
        calls: list[int] = []

        def fake_urlopen(req, timeout):
            offset = _offset(req)
            calls.append(offset)
            if offset == 0:
                return FakeResponse(json.dumps([{"timestamp": i, "type": "TRADE"} for i in range(500)]).encode("utf-8"))
            if offset == 3000:
                return FakeResponse(b"[]")
            if offset == 500:
                return FakeResponse(json.dumps([{"timestamp": 500 + i, "type": "TRADE"} for i in range(5)]).encode("utf-8"))
            return FakeResponse(b"[]")

        with patch.object(self.pull.urllib.request, "urlopen", side_effect=fake_urlopen):
            rows = self.pull.fetch_chunk(
                "0x1111111111111111111111111111111111111111",
                1000,
                1000 + 86400,
                500,
                1,
                0,
                0,
                0,
                86400,
                3000,
                500,
            )

        self.assertEqual(len(rows), 505)
        self.assertEqual(calls, [0, 3000, 500])


if __name__ == "__main__":
    unittest.main()
