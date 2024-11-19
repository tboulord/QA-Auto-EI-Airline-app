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



async def create_passenger(api_request_context: APIRequestContext, wiremock_admin_context: APIRequestContext, passport_id, first_name, last_name, flight_id="AAA01"):

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



async def delete_passenger(api_request_context: APIRequestContext, customer_id, flight_id="AAA01"):

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



def get_flight_by_id(flights, flight_id):
    """
    Helper function to get flight data by ID
    
    """
    for flight in flights:
        if flight["id"] == flight_id:
            return flight
    return None


def find_flight_with_different_timezones(flights):
    """
    Helper function to find a flight with different departure and arrival timezones
    
    """
    for flight in flights:
        if "departure_timezone" in flight and "arrival_timezone" in flight:
            return flight
    return None


def find_flight_with_same_timezone(flights):
    """
    Helper function to find a flight with same timezone
    
    """
    for flight in flights:
        if "timezone" in flight and "departure_timezone" not in flight:
            return flight
    return None


def get_test_customer(customers):
    """
    Helper function to get a test customer from the test data
    
    """
    if not customers:
        raise ValueError("No test customers available in test data")
    return customers[0]


def verify_passenger_in_list(passengers, customer_id):
    """
    Helper function to verify if a passenger exists in the list
    
    """
    return any(p["customer_id"] == customer_id for p in passengers)

