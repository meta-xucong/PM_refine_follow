from __future__ import annotations

import time
from typing import Any

import requests


class DataApiError(RuntimeError):
    pass


class RateLimiter:
    def __init__(self, min_interval_seconds: float = 0.0) -> None:
        self.min_interval_seconds = max(0.0, float(min_interval_seconds))
        self._last_call = 0.0

    def wait(self) -> None:
        if self.min_interval_seconds <= 0:
            return
        now = time.monotonic()
        delay = self.min_interval_seconds - (now - self._last_call)
        if delay > 0:
            time.sleep(delay)
        self._last_call = time.monotonic()


class DataApiClient:
    def __init__(
        self,
        base_url: str = "https://data-api.polymarket.com",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        sleep_seconds: float = 0.2,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_retries = max(0, int(max_retries))
        self.session = session or requests.Session()
        self.rate_limiter = RateLimiter(sleep_seconds)

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = self.base_url + (path if path.startswith("/") else f"/{path}")
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            self.rate_limiter.wait()
            try:
                response = self.session.get(
                    url,
                    params={k: v for k, v in (params or {}).items() if v is not None},
                    timeout=self.timeout_seconds,
                    headers={"User-Agent": "PM-refine-follow-auto-screen/1.0", "Accept": "application/json"},
                )
                if response.status_code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # pragma: no cover - exact requests errors vary
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
        raise DataApiError(f"GET {url} failed: {last_error}") from last_error

    def fetch_leaderboard(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.get("/v1/leaderboard", params)
        return extract_rows(payload)

    def fetch_activity(self, user: str, limit: int = 300, offset: int = 0, extra: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        params = {"user": user.lower(), "limit": limit, "offset": offset}
        params.update(extra or {})
        payload = self.get("/activity", params)
        return extract_rows(payload)

    def fetch_trades(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.get("/trades", params)
        return extract_rows(payload)

    def fetch_holders(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.get("/holders", params)
        return extract_rows(payload)


class GammaApiClient(DataApiClient):
    def __init__(
        self,
        base_url: str = "https://gamma-api.polymarket.com",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        sleep_seconds: float = 0.2,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            sleep_seconds=sleep_seconds,
            session=session,
        )

    def fetch_markets(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.get("/markets", params)
        return extract_rows(payload)


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "leaderboard", "users", "results", "value"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [x for x in rows if isinstance(x, dict)]
    return []
