import json
import logging
from playwright.async_api import APIRequestContext

logger = logging.getLogger(__name__)

async def setup_wiremock_stub(wiremock_admin_context: APIRequestContext, passport_id, first_name, last_name):
    """
    Set up a WireMock stub to simulate the Passport API for a customer.

    """
    logger.debug(f"Setting up Wiremock stub for passport_id={passport_id}, first_name={first_name}, last_name={last_name}")
    mapping = {
        "request": {
            "method": "GET",
            "url": "/passport",
            "bodyPatterns": [
                {
                    "equalToJson": json.dumps({"passport_id": passport_id}),
                    "ignoreArrayOrder": True,
                    "ignoreExtraElements": True
                }
            ]
        },
        "response": {
            "status": 200,
            "jsonBody": {
                "passport_id": passport_id,
                "first_name": first_name,
                "last_name": last_name
            }
        }
    }
    response = await wiremock_admin_context.post(
        "/__admin/mappings",
        data=json.dumps(mapping),
        headers={"Content-Type": "application/json"}
    )
    response_text = await response.text()
    assert response.status == 201, f"WireMock stub setup failed: {response_text}"


async def create_customer(api_request_context: APIRequestContext, wiremock_admin_context: APIRequestContext, passport_id, first_name, last_name, flight_id="AAA01"):
    """
    Create a customer and add them to a flight's passengers list.

    """
    await setup_wiremock_stub(wiremock_admin_context, passport_id, first_name, last_name)

    passenger_data = {"passport_id": passport_id, "first_name": first_name, "last_name": last_name}

    response = await api_request_context.post(
        f"/flights/{flight_id}/passengers",
        data=json.dumps(passenger_data),
        headers={"Content-Type": "application/json"}
    )
    response_text = await response.text()
    assert response.status == 200, f"Customer creation failed with status {response.status}, response: {response_text}"

    json_response = json.loads(response_text)
    customer_id = json_response["customer_id"]
    return customer_id


async def delete_customer(api_request_context: APIRequestContext, customer_id, flight_id="AAA01"):
    """
    Delete a customer from a flight's passengers list.

    """
    response = await api_request_context.delete(f"/flights/{flight_id}/passengers/{customer_id}")
    response_text = await response.text()
    assert response.status in [200, 204], f"Delete failed with status {response.status}, response: {response_text}"

    response = await api_request_context.get(f"/flights/{flight_id}/passengers")
    response_text = await response.text()
    json_response = json.loads(response_text)
    passengers = json_response.get("passengers", [])
    assert all(p["customer_id"] != customer_id for p in passengers), f"Customer ID {customer_id} still found in passengers list"
