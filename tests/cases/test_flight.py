import pytest
from playwright.async_api import APIRequestContext
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


from ..helpers.helpers import find_flight_with_different_timezones, get_flight_by_id, find_flight_with_same_timezone


@pytest.mark.asyncio
async def test_retrieve_flight_different_timezones(api_request_context: APIRequestContext, test_data):
    """
    Test Scenario:
    Retrieve flight details for a flight where the departure and arrival airports are in different timezones.

    """
    # Get a flight that has different departure and arrival timezones
    flight_data = find_flight_with_different_timezones(test_data["flights"])
    assert flight_data is not None, "No flight found with different timezones"
    

    response = await api_request_context.get("/flights")
    assert response.status == 200
    json_response = await response.json()
    flights = json_response.get("flights", [])

    
    flight = get_flight_by_id(flights, flight_data["id"])
    assert flight is not None, f"Flight '{flight_data['id']}' not found"

    departure_time = datetime.fromisoformat(flight["departure_time"])
    arrival_time = datetime.fromisoformat(flight["arrival_time"])
    
    original_departure_time_utc = datetime.fromisoformat(
        flight_data["departure_time_utc"]).replace(tzinfo=timezone.utc)
    original_arrival_time_utc = datetime.fromisoformat(
        flight_data["arrival_time_utc"]).replace(tzinfo=timezone.utc)
    
    expected_departure_time = original_departure_time_utc.astimezone(
        ZoneInfo(flight_data["departure_timezone"]))
    expected_arrival_time = original_arrival_time_utc.astimezone(
        ZoneInfo(flight_data["arrival_timezone"]))
    
    assert departure_time == expected_departure_time, "Departure time mismatch"
    assert arrival_time == expected_arrival_time, "Arrival time mismatch"


@pytest.mark.asyncio
async def test_retrieve_flight_same_timezone(api_request_context: APIRequestContext, test_data):
    """
    Test Scenario:
    Retrieve flight details for a flight where the departure and arrival airports are in the same timezone.

    """
    # Get a flight that has a single timezone
    flight_data = find_flight_with_same_timezone(test_data["flights"])
    assert flight_data is not None, "No flight found with same timezone"
    
    response = await api_request_context.get("/flights")
    assert response.status == 200
    json_response = await response.json()
    flights = json_response.get("flights", [])

    
    flight = get_flight_by_id(flights, flight_data["id"])
    assert flight is not None, f"Flight '{flight_data['id']}' not found"

    departure_time = datetime.fromisoformat(flight["departure_time"])
    arrival_time = datetime.fromisoformat(flight["arrival_time"])
    
    original_departure_time_utc = datetime.fromisoformat(
        flight_data["departure_time_utc"]).replace(tzinfo=timezone.utc)
    original_arrival_time_utc = datetime.fromisoformat(
        flight_data["arrival_time_utc"]).replace(tzinfo=timezone.utc)
    
    expected_departure_time = original_departure_time_utc.astimezone(
        ZoneInfo(flight_data["timezone"]))
    expected_arrival_time = original_arrival_time_utc.astimezone(
        ZoneInfo(flight_data["timezone"]))
    
    assert departure_time == expected_departure_time, "Departure time mismatch"
    assert arrival_time == expected_arrival_time, "Arrival time mismatch"

