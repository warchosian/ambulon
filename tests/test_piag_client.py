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
# Collection resolution tests
# ---------------------------------------------------------------------------

def test_resolve_collection_id_with_valid_id(bare_client, monkeypatch):
    """Test resolving collection when input looks like an ID and exists."""
    collection_id = "abc123def456789"  # Looks like ID (15 chars, alphanumeric)
    
    # Mock get_collection to succeed
    mock_get = MagicMock(return_value={"id": collection_id, "name": "Test Collection"})
    monkeypatch.setattr(bare_client, "get_collection", mock_get)
    
    result = bare_client.resolve_collection_id(collection_id, "project123")
    
    assert result == collection_id
    mock_get.assert_called_once_with(collection_id)


def test_resolve_collection_id_with_name(bare_client, monkeypatch):
    """Test resolving collection when input is a name."""
    collection_name = "My Test Collection"  # Clearly a name (has spaces)
    collection_id = "abc123def456789"
    
    # Mock list_collections to return matching collection
    mock_list = MagicMock(return_value={
        "items": [
            {"id": collection_id, "name": collection_name, "created_at": "2024-01-01"}
        ]
    })
    monkeypatch.setattr(bare_client, "list_collections", mock_list)
    
    result = bare_client.resolve_collection_id(collection_name, "project123")
    
    assert result == collection_id
    mock_list.assert_called_once_with("project123", limit=1000)


def test_resolve_collection_id_multiple_matches_uses_first(bare_client, monkeypatch):
    """Test resolving collection when multiple collections have same name."""
    collection_name = "Duplicate Name"
    collection_id1 = "abc123def456789"
    collection_id2 = "xyz789abc123456"
    
    # Mock list_collections to return multiple matches
    mock_list = MagicMock(return_value={
        "items": [
            {"id": collection_id1, "name": collection_name, "created_at": "2024-01-01"},
            {"id": collection_id2, "name": collection_name, "created_at": "2024-01-02"}
        ]
    })
    monkeypatch.setattr(bare_client, "list_collections", mock_list)
    
    # Use force=True to avoid stderr output in tests
    bare_client.force = True
    
    result = bare_client.resolve_collection_id(collection_name, "project123")
    
    assert result == collection_id1  # Should use first match


def test_resolve_collection_id_not_found_raises_error(bare_client, monkeypatch):
    """Test resolving collection when collection doesn't exist."""
    collection_name = "Nonexistent Collection"
    
    # Mock list_collections to return empty list
    mock_list = MagicMock(return_value={"items": []})
    monkeypatch.setattr(bare_client, "list_collections", mock_list)
    
    # Mock get_collection to raise 404
    mock_get = MagicMock(side_effect=requests.exceptions.HTTPError(
        response=MagicMock(status_code=404)
    ))
    monkeypatch.setattr(bare_client, "get_collection", mock_get)
    
    with pytest.raises(ValueError, match="Collection 'Nonexistent Collection' non trouvée"):
        bare_client.resolve_collection_id(collection_name, "project123")


def test_resolve_collection_id_empty_input_raises_error(bare_client):
    """Test resolving collection with empty input."""
    with pytest.raises(ValueError, match="Le nom ou l'ID de la collection ne peut pas être vide"):
        bare_client.resolve_collection_id("", "project123")


# ---------------------------------------------------------------------------
# Document resolution tests
# ---------------------------------------------------------------------------

def test_resolve_document_id_with_valid_id(bare_client, monkeypatch):
    """Test resolving document when input is already a valid ID."""
    document_id = "doc123abc456def"
    collection_id = "coll123"
    
    # Mock get_document to succeed
    mock_get = MagicMock(return_value={"id": document_id, "name": "test.pdf"})
    monkeypatch.setattr(bare_client, "get_document", mock_get)
    
    result = bare_client.resolve_document_id(document_id, collection_id)
    
    assert result == document_id
    mock_get.assert_called_once_with(collection_id, document_id)


def test_resolve_document_id_with_filename(bare_client, monkeypatch):
    """Test resolving document when input is a filename."""
    filename = "document.pdf"
    document_id = "doc123abc456def"
    collection_id = "coll123"
    
    # Mock get_document to fail (not an ID)
    mock_get = MagicMock(side_effect=requests.exceptions.HTTPError(
        response=MagicMock(status_code=404)
    ))
    monkeypatch.setattr(bare_client, "get_document", mock_get)
    
    # Mock list_documents to return matching document
    mock_list = MagicMock(return_value={
        "items": [
            {"id": document_id, "name": filename, "created_at": "2024-01-01"}
        ]
    })
    monkeypatch.setattr(bare_client, "list_documents", mock_list)
    
    result = bare_client.resolve_document_id(filename, collection_id)
    
    assert result == document_id
    mock_list.assert_called_once_with(collection_id, limit=1000)


def test_resolve_document_id_multiple_matches_uses_first(bare_client, monkeypatch):
    """Test resolving document when multiple documents have same name."""
    filename = "duplicate.pdf"
    document_id1 = "doc123abc456def"
    document_id2 = "doc789xyz123abc"
    collection_id = "coll123"
    
    # Mock get_document to fail (not an ID)
    mock_get = MagicMock(side_effect=requests.exceptions.HTTPError(
        response=MagicMock(status_code=404)
    ))
    monkeypatch.setattr(bare_client, "get_document", mock_get)
    
    # Mock list_documents to return multiple matches
    mock_list = MagicMock(return_value={
        "items": [
            {"id": document_id1, "name": filename, "created_at": "2024-01-01"},
            {"id": document_id2, "name": filename, "created_at": "2024-01-02"}
        ]
    })
    monkeypatch.setattr(bare_client, "list_documents", mock_list)
    
    # Use force=True to avoid stderr output in tests
    bare_client.force = True
    
    result = bare_client.resolve_document_id(filename, collection_id)
    
    assert result == document_id1  # Should use first match


def test_resolve_document_id_not_found_raises_error(bare_client, monkeypatch):
    """Test resolving document when document doesn't exist."""
    filename = "nonexistent.pdf"
    collection_id = "coll123"
    
    # Mock get_document to fail (not an ID)
    mock_get = MagicMock(side_effect=requests.exceptions.HTTPError(
        response=MagicMock(status_code=404)
    ))
    monkeypatch.setattr(bare_client, "get_document", mock_get)
    
    # Mock list_documents to return empty list
    mock_list = MagicMock(return_value={"items": []})
    monkeypatch.setattr(bare_client, "list_documents", mock_list)
    
    with pytest.raises(ValueError, match="Document 'nonexistent.pdf' non trouvé"):
        bare_client.resolve_document_id(filename, collection_id)


def test_resolve_document_id_empty_input_raises_error(bare_client):
    """Test resolving document with empty input."""
    with pytest.raises(ValueError, match="Le nom ou l'ID du document ne peut pas être vide"):
        bare_client.resolve_document_id("", "coll123")


# ---------------------------------------------------------------------------
# Search method tests
# ---------------------------------------------------------------------------

def test_search_with_single_collection_id(bare_client, monkeypatch):
    """Test search with a single collection_id parameter."""
    mock_request = MagicMock(return_value={"results": []})
    monkeypatch.setattr(bare_client, "_request", mock_request)
    
    bare_client.search(
        collection_id="coll123",
        query="test query",
        project_id="proj456"
    )
    
    # Verify _request was called with correct parameters
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    
    assert call_args.args[0] == "POST"  # method
    assert "/search" in call_args.args[1]  # endpoint
    assert call_args.kwargs["params"] == {"project_id": "proj456"}
    
    # Check payload
    import json
    payload = json.loads(call_args.kwargs["data"])
    assert payload["collections"] == ["coll123"]
    assert payload["query"] == "test query"


def test_search_with_collections_list(bare_client, monkeypatch):
    """Test search with a collections list parameter."""
    mock_request = MagicMock(return_value={"results": []})
    monkeypatch.setattr(bare_client, "_request", mock_request)
    
    bare_client.search(
        collections=["coll123", "coll456"],
        query="test query",
        project_id="proj789"
    )
    
    # Verify _request was called with correct parameters
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    
    # Check payload
    import json
    payload = json.loads(call_args.kwargs["data"])
    assert payload["collections"] == ["coll123", "coll456"]


def test_search_missing_collections_raises_error(bare_client):
    """Test search without collection_id or collections raises error."""
    with pytest.raises(ValueError, match="Vous devez fournir soit collection_id soit collections"):
        bare_client.search(query="test", project_id="proj123")


def test_search_missing_query_raises_error(bare_client):
    """Test search without query raises error."""
    with pytest.raises(ValueError, match="Le paramètre query est requis"):
        bare_client.search(collection_id="coll123", project_id="proj123")


def test_search_missing_project_id_raises_error(bare_client):
    """Test search without project_id raises error."""
    with pytest.raises(ValueError, match="Le paramètre project_id est requis"):
        bare_client.search(collection_id="coll123", query="test")


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
