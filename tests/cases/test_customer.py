import pytest
from playwright.async_api import APIRequestContext
import json
import logging

from ..helpers.helpers import create_passenger, delete_passenger, setup_wiremock_stub, get_test_customer


@pytest.mark.asyncio
async def test_update_customer_information(
    api_request_context: APIRequestContext,
    wiremock_admin_context: APIRequestContext,
    test_data
):
    """
    Test Scenario:
    Update the information of an existing customer and validate that the changes are correctly applied.
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
        # Update customer data
        updated_first_name = f"Updated_{first_name}"
        await setup_wiremock_stub(
            wiremock_admin_context, 
            passport_id, 
            updated_first_name, 
            last_name
        )

        updated_data = {
            "passport_id": passport_id,
            "first_name": updated_first_name,
            "last_name": last_name
        }

        # Send update request
        response = await api_request_context.put(
            f"/flights/{flight_id}/passengers/{customer_id}",
            data=json.dumps(updated_data),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 200

        # Verify response
        json_response = await response.json()
        assert json_response["first_name"] == updated_first_name

    finally:
        await delete_passenger(api_request_context, customer_id, flight_id)


@pytest.mark.asyncio
async def test_update_customer_with_mismatched_details(
    api_request_context: APIRequestContext,
    wiremock_admin_context: APIRequestContext,
    test_data
):
    """
    Test Scenario:
    Attempt to update a customer's information with details that do not match the Passport API, 
    and verify that the update is rejected.
    """
    # Get test customer data
    customer_data = get_test_customer(test_data["customers"])
    passport_id = customer_data["passport_id"]
    first_name = customer_data["first_name"]
    last_name = customer_data["last_name"]
    flight_id = customer_data.get("flight_id")
    assert flight_id is not None, "Flight ID is missing in test data"

    # Create test passenger
    customer_id = await create_passenger(
        api_request_context, 
        wiremock_admin_context, 
        passport_id, 
        first_name, 
        last_name, 
        flight_id
    )

    try:
        passport_api_first_name = f"PassportAPI_{first_name}"
        await setup_wiremock_stub(
            wiremock_admin_context, 
            passport_id, 
            passport_api_first_name, 
            last_name
        )

        update_request_first_name = f"Request_{first_name}"
        updated_data = {
            "passport_id": passport_id,
            "first_name": update_request_first_name,
            "last_name": last_name
        }

        response = await api_request_context.put(
            f"/flights/{flight_id}/passengers/{customer_id}",
            data=json.dumps(updated_data),
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 400

        json_response = await response.json()
        expected_error = "Firstname or Lastname is mismatch."
        assert json_response["detail"] == expected_error

    finally:
        await delete_passenger(api_request_context, customer_id, flight_id)