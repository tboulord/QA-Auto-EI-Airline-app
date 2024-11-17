# test_flight.py

import pytest
from playwright.async_api import APIRequestContext
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


@pytest.mark.asyncio
async def test_retrieve_flight_different_timezones(api_request_context: APIRequestContext, test_data):
    """
    Test Scenario:
    Retrieve flight details for a flight where the departure and arrival airports are in different timezones.

    """
    flight_data = next(f for f in test_data["flights"] if f["id"] == "BBB02")
    response = await api_request_context.get("/flights")
    assert response.status == 200
    json_response = await response.json()
    flights = json_response.get("flights", [])
    flight = next((f for f in flights if f["id"] == "BBB02"), None)
    assert flight is not None, "Flight 'BBB02' not found"
    departure_time_str = flight["departure_time"]
    arrival_time_str = flight["arrival_time"]
    departure_time = datetime.fromisoformat(departure_time_str)
    arrival_time = datetime.fromisoformat(arrival_time_str)
    original_departure_time_utc = datetime.fromisoformat(flight_data["departure_time_utc"]).replace(tzinfo=timezone.utc)
    original_arrival_time_utc = datetime.fromisoformat(flight_data["arrival_time_utc"]).replace(tzinfo=timezone.utc)
    expected_departure_time = original_departure_time_utc.astimezone(ZoneInfo(flight_data["departure_timezone"]))
    expected_arrival_time = original_arrival_time_utc.astimezone(ZoneInfo(flight_data["arrival_timezone"]))
    assert departure_time == expected_departure_time, "Departure time mismatch"
    assert arrival_time == expected_arrival_time, "Arrival time mismatch"


@pytest.mark.asyncio
async def test_retrieve_flight_same_timezone(api_request_context: APIRequestContext, test_data):
    """
    Test Scenario:
    Retrieve flight details for a flight where the departure and arrival airports are in the same timezone.

    """
    flight_data = next(f for f in test_data["flights"] if f["id"] == "AAA01")
    response = await api_request_context.get("/flights")
    assert response.status == 200
    json_response = await response.json()
    flights = json_response.get("flights", [])
    flight = next((f for f in flights if f["id"] == "AAA01"), None)
    assert flight is not None, "Flight 'AAA01' not found"
    departure_time_str = flight["departure_time"]
    arrival_time_str = flight["arrival_time"]
    departure_time = datetime.fromisoformat(departure_time_str)
    arrival_time = datetime.fromisoformat(arrival_time_str)
    original_departure_time_utc = datetime.fromisoformat(flight_data["departure_time_utc"]).replace(tzinfo=timezone.utc)
    original_arrival_time_utc = datetime.fromisoformat(flight_data["arrival_time_utc"]).replace(tzinfo=timezone.utc)
    expected_departure_time = original_departure_time_utc.astimezone(ZoneInfo(flight_data["timezone"]))
    expected_arrival_time = original_arrival_time_utc.astimezone(ZoneInfo(flight_data["timezone"]))
    assert departure_time == expected_departure_time, "Departure time mismatch"
    assert arrival_time == expected_arrival_time, "Arrival time mismatch"
