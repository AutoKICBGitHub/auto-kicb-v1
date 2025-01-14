import pytest
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_invalid_login(driver):
    login_page = LoginPage(driver)
    login_page.enter_username("invalid_user")
    login_page.enter_password("invalid_password")
    login_page.tap_login_button()
    assert login_page.is_error_visible(), "Ошибка входа не отображается"


def test_login(driver):
    # Найти элемент по accessibility id
    username_field = driver.find_element_by_accessibility_id("username_input")
    password_field = driver.find_element_by_accessibility_id("password_input")
    login_button = driver.find_element_by_accessibility_id("login_button")
    
    # Ввести данные
    username_field.send_keys("test@example.com")
    password_field.send_keys("password123")
    
    # Нажать кнопку
    login_button.click()
    
    # Проверить результат
    success_message = driver.find_element_by_accessibility_id("success_message")
    assert success_message.is_displayed()
