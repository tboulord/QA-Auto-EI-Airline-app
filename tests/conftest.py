import pytest
import pytest_asyncio
from playwright.async_api import Playwright, APIRequestContext, async_playwright
import asyncio
import json
import os
import logging
from _pytest.reports import TestReport

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to customize the test report.

    """
    outcome = yield
    report: TestReport = outcome.get_result()

    if report.when == "call":
        if report.passed:
            status = "PASSED"
        elif report.failed:
            status = "FAILED"
        else:
            status = "SKIPPED"

        item.user_properties.append(("status", status))

        if "test_data" in item.fixturenames:
            data = item.funcargs["test_data"]
            item.user_properties.append(("test_data", str(data)))

        logger.debug(f"Test case '{item.name}' completed with status: {status}")


@pytest.fixture(scope="session")
def event_loop():
    """
    Provides an event loop for asynchronous test execution.

    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def playwright_instance() -> Playwright:
    """
    Provides a Playwright instance for the session.

    """
    async with async_playwright() as playwright:
        yield playwright


@pytest_asyncio.fixture(scope='function')
async def api_request_context(playwright_instance: Playwright) -> APIRequestContext:
    logger.debug("Initializing API request context...")
    request_context = await playwright_instance.request.new_context(base_url="http://airline_api_dev:8000")
    yield request_context
    logger.debug("Disposing API request context...")
    await request_context.dispose()


@pytest_asyncio.fixture(scope='session')
async def wiremock_admin_context(playwright_instance: Playwright) -> APIRequestContext:
    """
    Provides an APIRequestContext for the WireMock admin API.

    """
    request_context = await playwright_instance.request.new_context(base_url="http://passport_api:8080")
    yield request_context
    await request_context.dispose()


@pytest_asyncio.fixture(autouse=True)
async def reset_wiremock(wiremock_admin_context: APIRequestContext):
    """
    Automatically resets WireMock stubs before each test.

    """
    await wiremock_admin_context.post("/__admin/reset")
    yield


@pytest.fixture(scope="session")
def test_data():
    """
    Loads and provides test data from a JSON file.

    """
    data_file = os.path.join(os.path.dirname(__file__), './datas/test_data.json')
    data_file = os.path.abspath(data_file)
    with open(data_file) as f:
        data = json.load(f)
    return data
