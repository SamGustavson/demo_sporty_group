"""Shared fixtures: a clean per-test user state, an API client and a Chrome driver."""
from datetime import datetime, UTC
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from core.api.client import ApiClient
from core.config import settings
from core.constants import HttpStatus

ARTIFACTS = Path(__file__).resolve().parent.parent / "screenshots"


@pytest.fixture(scope="session")
def api() -> ApiClient:
    return ApiClient()


@pytest.fixture(autouse=True)
def clean_balance(api: ApiClient):
    """Every test starts from the initial balance so tests are order-independent."""
    response = api.reset_balance()
    assert response.status_code == HttpStatus.OK, f"reset-balance failed: {response.status_code} {response.text}"
    yield

@pytest.fixture
def balance_before(api: ApiClient) -> float:
    return api.balance_value()


@pytest.fixture
def upcoming_match(api: ApiClient) -> dict:
    """First match that kicks off after today (the app also lists PAST matches)."""
    response = api.get_matches()
    assert response.status_code == HttpStatus.OK, f"GET /api/matches failed: {response.status_code}"
    today = datetime.now(UTC).date().isoformat()
    upcoming = [match for match in response.json() if match["kickoffDate"] > today]
    assert upcoming, "Precondition failed: the API returned no upcoming matches"
    return upcoming[0]


@pytest.fixture
def driver(request):
    options = Options()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1600,1000")
    drv = webdriver.Chrome(options=options)  # Selenium Manager resolves the driver binary
    yield drv
    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        ARTIFACTS.mkdir(exist_ok=True)
        drv.save_screenshot(str(ARTIFACTS / f"{request.node.name}.png"))
    drv.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
