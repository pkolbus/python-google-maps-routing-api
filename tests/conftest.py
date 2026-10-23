"""Fixtures for the Google Maps Routes API tests."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from google_maps_routing_api import GoogleMapsRoutingApi
from google_maps_routing_api import api as api_module

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

API_KEY = "test-api-key"
REFERRER = "https://example.com/"
ORIGIN_ADDRESS = "Mountain View, CA"
DESTINATION_ADDRESS = "San Francisco, CA"
ORIGIN_LAT = 37.42
ORIGIN_LNG = -122.08

_FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture recorded from the real API."""
    data: dict[str, Any] = json.loads((_FIXTURES / f"{name}.json").read_text())
    return data


@dataclass
class RecordedRequest:
    """A request received by the mock server."""

    path: str
    query: dict[str, str]
    headers: dict[str, str]
    json: Any


@dataclass
class MockServer:
    """A stand-in for the Google Maps Routes API that records requests and replays responses."""

    requests: list[RecordedRequest] = field(default_factory=list)
    _responses: deque[tuple[int, Any]] = field(default_factory=deque)

    def add_response(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        """Queue a response to return, in order, for the next request."""
        self._responses.append((status, payload))

    async def handle(self, request: web.Request) -> web.Response:
        """Record the request and return the next queued response."""
        self.requests.append(
            RecordedRequest(
                path=request.path,
                query=dict(request.query),
                headers=dict(request.headers),
                json=await request.json(),
            )
        )
        if not self._responses:
            pytest.fail(f"Unexpected request to {request.path}")
        status, payload = self._responses.popleft()
        if isinstance(payload, str):
            return web.Response(status=status, text=payload, content_type="text/html")
        return web.json_response(payload, status=status)


@pytest.fixture
async def mock_server(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[MockServer]:
    """Run a local server in place of the Google Maps Routes API."""
    server = MockServer()
    app = web.Application()
    app.router.add_post("/{tail:.*}", server.handle)
    test_server = TestServer(app)
    await test_server.start_server()
    monkeypatch.setattr(api_module, "_BASE_URL", str(test_server.make_url("")))
    yield server
    await test_server.close()


@pytest.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession]:
    """Return an aiohttp client session."""
    async with aiohttp.ClientSession() as client_session:
        yield client_session


@pytest.fixture
def api(session: aiohttp.ClientSession) -> GoogleMapsRoutingApi:
    """Return a Google Maps Routes API client."""
    return GoogleMapsRoutingApi(session=session, api_key=API_KEY, referrer=REFERRER)
