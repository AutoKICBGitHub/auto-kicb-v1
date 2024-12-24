import pytest
from playwright.sync_api import sync_playwright
from pages.base_login_flow import Login_flow

@pytest.fixture(scope="function")
def browser():
    """Настройка браузера."""  # ЗАДАТЬ: параметры настройки браузера
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        user_data_dir = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default"  # Замените на путь к вашему профилю
            # Используем launch_persistent_context для открытия браузера с пользовательским профилем
        context = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False  # Открываем браузер в обычном режиме
            )
        page = context.new_page()
        page.goto("https://ibank.kicb.net/")
        login_flow = Login_flow()
        login_flow.test_login_flow(page)
        yield page
        
        context.close()
        browser.close()
