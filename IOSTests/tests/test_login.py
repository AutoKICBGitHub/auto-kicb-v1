import pytest
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_invalid_login(driver):
    login_page = LoginPage(driver)
    login_page.enter_username("invalid_user")
    login_page.enter_password("invalid_password")
    login_page.tap_login_button()
    assert login_page.is_error_visible(), "Ошибка входа не отображается"
