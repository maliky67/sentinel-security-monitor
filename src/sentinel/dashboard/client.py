"""HTTP client for Sentinel's local FastAPI backend."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from uuid import UUID

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 5


class SentinelAPIError(Exception):
    """Raised when Sentinel's API cannot be reached or read."""


def fetch_json(
    endpoint: str,
    params: dict[str, str | int] | None = None,
) -> dict:
    """Retrieve JSON from the local Sentinel API."""
    if not endpoint.startswith("/") or endpoint.startswith("//"):
        raise ValueError("Endpoint must be a relative API path")

    query = f"?{urlencode(params)}" if params else ""
    url = f"{API_BASE_URL}{endpoint}{query}"

    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            data = json.load(response)

    except HTTPError as error:
        raise SentinelAPIError(f"API returned HTTP {error.code}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise SentinelAPIError(
            "Cannot connect to Sentinel API at 127.0.0.1:8000"
        ) from error
    except (json.JSONDecodeError, UnicodeError) as error:
        raise SentinelAPIError("API returned an invalid JSON response") from error

    if not isinstance(data, dict):
        raise SentinelAPIError("Unexpected API response format")

    return data


def get_health() -> dict:
    return fetch_json("/health")


def get_summary() -> dict:
    return fetch_json("/stats/summary")


def get_events(
    limit: int = 100,
    offset: int = 0,
    outcome: str | None = None,
) -> dict:
    params: dict[str, str | int] = {
        "limit": limit,
        "offset": offset,
    }

    if outcome:
        params["outcome"] = outcome

    return fetch_json("/events", params)


def get_alerts(
    limit: int = 100,
    offset: int = 0,
    severity: str | None = None,
) -> dict:
    params: dict[str, str | int] = {
        "limit": limit,
        "offset": offset,
    }

    if severity:
        params["severity"] = severity

    return fetch_json("/alerts", params)


def get_alert(alert_id: str) -> dict:
    """Retrieve one alert after validating its identifier."""
    validated_id = UUID(alert_id)
    return fetch_json(f"/alerts/{validated_id}")
