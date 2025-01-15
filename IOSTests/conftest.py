import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from utils.capabilities import get_ios_simulator_capabilities
from pages.login_page import LoginPage
from pages.otp_page import OTPPage
from selenium.common.exceptions import NoSuchElementException


def is_user_logged_in(driver):
    """Проверка, авторизован ли пользователь"""
    try:
        # Проверяем наличие имени пользователя на главном экране
        user_name = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Ырысбеков Атай Айбекович")
        return user_name.is_displayed()
    except NoSuchElementException:
        return False


def is_login_required(driver):
    """Проверка, нужен ли логин"""
    try:
        # Проверяем наличие поля для ввода логина
        login_field = driver.find_element(
            AppiumBy.XPATH, 
            "//XCUIElementTypeSecureTextField[@value='Логин']"
        )
        return login_field.is_displayed()
    except NoSuchElementException:
        return False


@pytest.fixture(scope="session")
def driver():
    # Инициализация драйвера
    caps = get_ios_simulator_capabilities()
    options = XCUITestOptions()
    for key, value in caps.items():
        options.set_capability(key, value)
    
    driver = None
    try:
        driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            options=options
        )
        yield driver
    finally:
        if driver:
            driver.quit()


@pytest.fixture(scope="function")
def setup(driver):
    # Проверяем, авторизован ли пользователь
    if is_user_logged_in(driver):
        print("✅ Пользователь уже авторизован, пропускаем шаги логина")
        yield
        return
        
    # Проверяем, нужен ли логин
    if is_login_required(driver):
        # Логин
        login_page = LoginPage(driver)
        login_page.login_as_valid_user()
        
        # Ввод OTP
        otp_page = OTPPage(driver)
        assert otp_page.is_page_displayed(), "Страница OTP не отображается"
        otp_page.enter_otp()
    else:
        print("ℹ️ Форма логина не найдена, возможно пользователь уже авторизован")
    
    yield
