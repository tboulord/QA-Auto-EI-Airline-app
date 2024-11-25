import pytest
from playwright.async_api import APIRequestContext
import json
import logging


from ..helpers.helpers import create_passenger, delete_passenger, setup_wiremock_stub, get_test_customer, verify_passenger_in_list



@pytest.mark.asyncio
async def test_create_flight_booking_with_valid_customer(
    api_request_context: APIRequestContext,
    wiremock_admin_context: APIRequestContext,
    test_data
):
    """
    Test Scenario:
    Create a flight booking with a valid customer and verify that the booking is successfully created.

    """

    customer_data = get_test_customer(test_data["customers"])
    passport_id = customer_data["passport_id"]
    first_name = customer_data["first_name"]
    last_name = customer_data["last_name"]
    flight_id = customer_data.get("flight_id")
    assert flight_id is not None, "Flight ID is missing in test data"

    customer_id = await create_passenger(
        api_request_context,
        wiremock_admin_context,
        passport_id,
        first_name,
        last_name,
        flight_id

    )

    try:
        response = await api_request_context.get(f"/flights/{flight_id}/passengers")
        assert response.status == 200

        json_response = await response.json()
        passengers = json_response.get("passengers", [])

        assert verify_passenger_in_list(passengers, customer_id), \
            "Customer not found in passengers list"
    finally:
        await delete_passenger(api_request_context, customer_id, flight_id)



@pytest.mark.asyncio
async def test_create_booking_with_mismatched_customer_name(
    api_request_context: APIRequestContext,
    wiremock_admin_context: APIRequestContext,
    test_data
):
    """
    Test Scenario:
    Attempt to create a flight booking with a mismatched customer name and verify that the booking fails.

    """

    customer_data = get_test_customer(test_data["customers"])
    passport_id = customer_data["passport_id"]
    correct_first_name = customer_data["first_name"]
    last_name = customer_data["last_name"]
    flight_id = customer_data.get("flight_id")
    assert flight_id is not None, "Flight ID is missing in test data"

    await setup_wiremock_stub(
        wiremock_admin_context,
        passport_id,
        correct_first_name,
        last_name
    )

    incorrect_first_name = f"Incorrect_{correct_first_name}"
    passenger_data = {
        "passport_id": passport_id,
        "first_name": incorrect_first_name,
        "last_name": last_name
    }


    response = await api_request_context.post(
        f"/flights/{flight_id}/passengers",
        data=json.dumps(passenger_data),
        headers={"Content-Type": "application/json"}
    )

    assert response.status == 400
    json_response = await response.json()
    expected_error = "Firstname or Lastname is mismatch."
    assert json_response["detail"] == expected_error


@pytest.mark.asyncio
async def test_delete_valid_booking(
    api_request_context: APIRequestContext,
    wiremock_admin_context: APIRequestContext,
    test_data
):
    """
    Test Scenario:
    Delete a valid flight booking and verify that the booking is successfully removed.

    """


    customer_data = get_test_customer(test_data["customers"])
    passport_id = customer_data["passport_id"]
    first_name = customer_data["first_name"]
    last_name = customer_data["last_name"]
    flight_id = customer_data.get("flight_id")
    assert flight_id is not None, "Flight ID is missing in test data"

    customer_id = await create_passenger(
        api_request_context,
        wiremock_admin_context,
        passport_id,
        first_name,
        last_name,
        flight_id
    )

    await delete_passenger(api_request_context, customer_id, flight_id)

    list_response = await api_request_context.get(
        f"/flights/{flight_id}/passengers"
    )
    assert list_response.status == 200
    
    passengers = (await list_response.json()).get("passengers", [])
    assert not verify_passenger_in_list(passengers, customer_id), \
        "Customer still exists in passengers list after deletion"

