"""Unit tests for ``app.piag.core.client.PIAGClient``.

Covers the transport layer (session, retries, timeouts, error paths) with
``requests_mock``-style monkeypatching of the underlying session, so no real
network traffic is produced. The collection / document / search methods are
thin wrappers around ``_request`` so covering the retry loop + header merging
is enough.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
import requests

from app.piag.core import client as client_module
from app.piag.core.client import DEFAULT_MAX_RETRIES, RETRY_SLEEP_SECONDS, PIAGClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(
    status_code: int = 200,
    json_body: Dict[str, Any] | None = None,
    text_body: str | None = None,
) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if json_body is not None:
        resp.json.return_value = json_body
        resp.text = json.dumps(json_body)
    else:
        resp.json.side_effect = ValueError("not json")
        resp.text = text_body or ""
    # raise_for_status behaves like the real one: 4xx/5xx raise.
    if status_code >= 400:
        http_err = requests.exceptions.HTTPError(response=resp)
        resp.raise_for_status.side_effect = http_err
    else:
        resp.raise_for_status.return_value = None
    return resp


@pytest.fixture
def bare_client():
    """A client that ignores the ambient YAML and uses an explicit config."""
    return PIAGClient(
        api_token="test-token",
        base_url="https://api.example.local",
        config={
            "piag": {
                "rag": {
                    "api": {"max_retries": 2, "timeout": 5},
                    "logging": {"log_requests": False, "log_responses": False},
                }
            }
        },
    )


@pytest.fixture
def no_sleep(monkeypatch):
    """Drop the retry sleep so the test suite doesn't block on delays."""
    monkeypatch.setattr(client_module.time, "sleep", lambda _s: None)


# ---------------------------------------------------------------------------
# Constants & construction
# ---------------------------------------------------------------------------

def test_default_retry_constants_are_exported():
    assert DEFAULT_MAX_RETRIES == 3
    assert RETRY_SLEEP_SECONDS == 2


def test_client_initialises_session(bare_client):
    assert isinstance(bare_client._session, requests.Session)
    assert bare_client.api_token == "test-token"
    assert bare_client.base_url == "https://api.example.local"
    assert bare_client.timeout == 5
    assert bare_client.max_retries == 2


def test_client_is_context_manager_and_closes_session(bare_client):
    with bare_client as c:
        assert c is bare_client
    # After __exit__, the session should have been closed. requests.Session
    # does not toggle a boolean, but close() is idempotent; calling it twice
    # must stay safe.
    assert c.close() is None


# ---------------------------------------------------------------------------
# _request: happy path
# ---------------------------------------------------------------------------

def test_request_returns_json_body_on_200(bare_client, monkeypatch):
    mock_request = MagicMock(return_value=_make_response(200, {"items": [1, 2]}))
    monkeypatch.setattr(bare_client._session, "request", mock_request)

    result = bare_client._request("GET", "/api/v1/things")

    assert result == {"items": [1, 2]}
    mock_request.assert_called_once()
    call_kwargs = mock_request.call_args
    assert call_kwargs.args[0] == "GET"
    assert call_kwargs.args[1] == "https://api.example.local/api/v1/things"
    assert call_kwargs.kwargs["timeout"] == 5
    # Bearer token is injected.
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer test-token"


def test_request_returns_empty_dict_on_204(bare_client, monkeypatch):
    resp = _make_response(204)
    monkeypatch.setattr(bare_client._session, "request", MagicMock(return_value=resp))
    assert bare_client._request("DELETE", "/api/v1/things/42") == {}


def test_request_strips_trailing_slash_from_base_url(monkeypatch):
    c = PIAGClient(
        api_token="t",
        base_url="https://api.example.local/",
        config={"piag": {"rag": {"api": {"max_retries": 1}}}},
    )
    mock = MagicMock(return_value=_make_response(200, {}))
    monkeypatch.setattr(c._session, "request", mock)
    c._request("GET", "/x")
    assert mock.call_args.args[1] == "https://api.example.local/x"


def test_request_respects_extra_headers(bare_client, monkeypatch):
    mock = MagicMock(return_value=_make_response(200, {}))
    monkeypatch.setattr(bare_client._session, "request", mock)
    bare_client._request("GET", "/x", headers={"X-Custom": "42"})
    sent_headers = mock.call_args.kwargs["headers"]
    assert sent_headers["X-Custom"] == "42"
    assert sent_headers["Authorization"] == "Bearer test-token"


def test_request_include_content_type_toggles_header(monkeypatch):
    c = PIAGClient(
        api_token="t",
        base_url="https://api.example.local",
        config={"piag": {"rag": {"api": {"max_retries": 1}}}},
    )
    mock = MagicMock(return_value=_make_response(200, {}))
    monkeypatch.setattr(c._session, "request", mock)
    c._request("POST", "/x", include_content_type=True, data="{}")
    assert mock.call_args.kwargs["headers"].get("Content-Type") == "application/json"


# ---------------------------------------------------------------------------
# _request: retry & error paths
# ---------------------------------------------------------------------------

def test_request_retries_on_timeout_then_succeeds(bare_client, monkeypatch, no_sleep):
    """First call times out, second returns 200 -> final result wins."""
    calls: List[Any] = []

    def fake_request(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise requests.exceptions.Timeout("boom")
        return _make_response(200, {"ok": True})

    monkeypatch.setattr(bare_client._session, "request", fake_request)
    assert bare_client._request("GET", "/x") == {"ok": True}
    assert len(calls) == 2


def test_request_raises_last_timeout_when_all_retries_fail(
    bare_client, monkeypatch, no_sleep
):
    def fake_request(*args, **kwargs):
        raise requests.exceptions.Timeout("boom")

    monkeypatch.setattr(bare_client._session, "request", fake_request)
    with pytest.raises(requests.exceptions.Timeout):
        bare_client._request("GET", "/x")


def test_request_does_not_retry_on_http_error(bare_client, monkeypatch, no_sleep):
    """Non-timeout RequestException must surface immediately (no retry)."""
    call_count = 0

    def fake_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _make_response(404, text_body="not found")

    monkeypatch.setattr(bare_client._session, "request", fake_request)
    with pytest.raises(requests.exceptions.HTTPError):
        bare_client._request("GET", "/x")
    assert call_count == 1  # raised on first attempt, no retry


def test_request_sleeps_between_retries_with_configured_delay(
    bare_client, monkeypatch
):
    sleeps: List[float] = []
    monkeypatch.setattr(client_module.time, "sleep", lambda s: sleeps.append(s))

    def fake_request(*args, **kwargs):
        raise requests.exceptions.Timeout("boom")

    monkeypatch.setattr(bare_client._session, "request", fake_request)
    with pytest.raises(requests.exceptions.Timeout):
        bare_client._request("GET", "/x")
    # max_retries=2 -> one sleep between attempts 1 and 2.
    assert sleeps == [RETRY_SLEEP_SECONDS]
