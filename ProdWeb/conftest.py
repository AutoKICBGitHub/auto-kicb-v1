import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="function")
def browser():
    """Настройка браузера."""  # ЗАДАТЬ: параметры настройки браузера
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
