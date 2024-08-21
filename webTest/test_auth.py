import pytest
import playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "storage_state": {
            "cookies": [
                {
                    "name": "agerimk",
                    "value": "password1",
                    "url": "https://newibanktest.kicb.net/login"
                },
            ]
        },
    }
