import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from utils.capabilities import get_ios_simulator_capabilities
from pages.base_page import BasePage


@pytest.fixture(scope="session")
def driver():
    # Инициализация драйвера
    caps = get_ios_simulator_capabilities()
    options = XCUITestOptions()
    for key, value in caps.items():
        options.set_capability(key, value)
    
    try:
        driver = webdriver.Remote(
            command_executor='http://localhost:4724/wd/hub',
            options=options
        )
        
        # Обработка начальных алертов
        base_page = BasePage(driver)
        base_page.handle_alerts()
        
        yield driver
    finally:
        if driver:
            driver.quit()


@pytest.fixture(scope="function")
def setup():
    # Подготовка перед каждым тестом
    yield
    # Очистка после каждого теста
