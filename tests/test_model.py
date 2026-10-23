"""Tests for the Google Maps Routes API models."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

import pytest

from google_maps_routing_api import (
    ComputeRoutesResponse,
    LatLng,
    Location,
    RoutingPreference,
    TrafficModel,
    TransitRoutingPreference,
    TransitTravelMode,
    TravelMode,
    Units,
    Waypoint,
)

from .conftest import load_fixture

if TYPE_CHECKING:
    from google_maps_routing_api.model import ApiStrEnum

_RESPONSES = [
    "compute_routes_drive",
    "compute_routes_drive_metric",
    "compute_routes_transit",
]

_ENUMS = [
    RoutingPreference,
    TrafficModel,
    TransitRoutingPreference,
    TransitTravelMode,
    TravelMode,
    Units,
]


@pytest.mark.parametrize("fixture", _RESPONSES)
def test_parses_real_responses(fixture: str) -> None:
    """Test responses recorded from the real API parse."""
    assert ComputeRoutesResponse.from_dict(load_fixture(fixture))


@pytest.mark.parametrize("fixture", _RESPONSES)
def test_serializes_using_api_names(fixture: str) -> None:
    """Test to_dict uses the camelCase names the API uses."""
    parsed = ComputeRoutesResponse.from_dict(load_fixture(fixture))

    route = parsed.to_dict()["routes"][0]
    assert "distanceMeters" in route
    assert "staticDuration" in route
    assert "legs" in route
    assert "localizedValues" in route["legs"][0]


@pytest.mark.parametrize("fixture", _RESPONSES)
def test_round_trips(fixture: str) -> None:
    """Test a serialized model can be parsed back into an identical model."""
    parsed = ComputeRoutesResponse.from_dict(load_fixture(fixture))

    assert ComputeRoutesResponse.from_dict(parsed.to_dict()) == parsed


def test_parse_durations() -> None:
    """Test proto JSON durations parse into timedeltas."""
    parsed = ComputeRoutesResponse.from_dict({"routes": [{"duration": "581s"}]})
    assert parsed.routes[0].duration == datetime.timedelta(seconds=581)

    parsed = ComputeRoutesResponse.from_dict({"routes": [{"duration": "581.500s"}]})
    assert parsed.routes[0].duration == datetime.timedelta(seconds=581.5)

    parsed = ComputeRoutesResponse.from_dict({"routes": [{"staticDuration": "581s"}]})
    assert parsed.routes[0].static_duration == datetime.timedelta(seconds=581)
    assert parsed.routes[0].duration is None


def test_duration_none_is_tolerated() -> None:
    """Test a missing or null duration parses as None."""
    parsed = ComputeRoutesResponse.from_dict({"routes": [{"duration": None, "distanceMeters": 100}]})

    assert parsed.routes[0].duration is None
    assert parsed.routes[0].distance_meters == 100


def test_serialize_durations() -> None:
    """Test timedeltas serialize back into the proto JSON Duration format."""
    parsed = ComputeRoutesResponse.from_dict({"routes": [{"duration": "581s", "staticDuration": "581.500s"}]})

    assert parsed.to_dict()["routes"][0]["duration"] == "581s"
    assert parsed.to_dict()["routes"][0]["staticDuration"] == "581.5s"


def test_empty_response() -> None:
    """Test the empty response body returned when no route is found."""
    assert ComputeRoutesResponse.from_dict({}).routes == []


def test_deserializes_snake_case_names() -> None:
    """Test field names are accepted alongside the API's camelCase aliases."""
    parsed = ComputeRoutesResponse.from_dict({"routes": [{"distance_meters": 100, "static_duration": "60s"}]})

    assert parsed.routes[0].distance_meters == 100
    assert parsed.routes[0].static_duration == datetime.timedelta(seconds=60)


def test_ignores_unknown_fields() -> None:
    """Test fields the API adds later are ignored rather than failing the whole response."""
    data = load_fixture("compute_routes_drive")
    data["routes"][0]["someFieldAddedLater"] = {"nested": 1}

    assert ComputeRoutesResponse.from_dict(data).routes[0].distance_meters == 3197


def test_unknown_enum_value_falls_back(caplog: pytest.LogCaptureFixture) -> None:
    """Test a travel mode the API adds later does not fail the whole response."""
    with caplog.at_level(logging.WARNING, logger="google_maps_routing_api"):
        assert TravelMode("SOME_NEW_TRAVEL_MODE") is TravelMode.TRAVEL_MODE_UNSPECIFIED

    assert "SOME_NEW_TRAVEL_MODE" in caplog.text


@pytest.mark.parametrize("enum", _ENUMS)
def test_enums_fall_back_to_unspecified(enum: type[ApiStrEnum]) -> None:
    """Test every enum tolerates unknown values.

    The fallback returns the first member, so guard the convention that it is the
    ``*_UNSPECIFIED`` one.
    """
    first = next(iter(enum))

    assert first.name.endswith("UNSPECIFIED")
    assert enum("VALUE_ADDED_BY_GOOGLE_LATER") is first
    assert enum(None) is first  # type: ignore[arg-type]


def test_waypoint_round_trips() -> None:
    """Test waypoints serialize using the API's camelCase names, without unset fields."""
    assert Waypoint(address="Mountain View, CA").to_dict() == {"address": "Mountain View, CA"}
    assert Waypoint(place_id="ChIJj61dQgK0j4AR1Ge1WpwGfi8").to_dict() == {"placeId": "ChIJj61dQgK0j4AR1Ge1WpwGfi8"}
    assert Waypoint(location=Location(lat_lng=LatLng(latitude=1.0, longitude=2.0))).to_dict() == {
        "location": {"latLng": {"latitude": 1.0, "longitude": 2.0}}
    }
    assert Waypoint(location=Location(lat_lng=LatLng(latitude=1.0, longitude=2.0), heading=270)).to_dict() == {
        "location": {"latLng": {"latitude": 1.0, "longitude": 2.0}, "heading": 270}
    }


def test_empty_localized_text() -> None:
    """Test a localized text without any fields set parses."""
    parsed = ComputeRoutesResponse.from_dict({"routes": [{"localizedValues": {"duration": {}}}]})

    assert parsed.routes[0].localized_values is not None
    assert parsed.routes[0].localized_values.duration is not None
    assert parsed.routes[0].localized_values.duration.text is None
    assert parsed.routes[0].localized_values.duration.language_code is None
