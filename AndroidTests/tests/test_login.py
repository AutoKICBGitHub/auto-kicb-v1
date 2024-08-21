import pytest
import time
from AndroidTests.pages.login_page import LoginPage
from AndroidTests.pages.otp_page import OTPPage
# from androidTest.pages.home_page import HomePage
from AndroidTests.users import get_user


@pytest.fixture()
def driver(appium_driver):
    return appium_driver

def test_login(driver):

    user = get_user('ataiyr')

    login_page = LoginPage(driver)

    # home_page = HomePage(driver)

    login_page.enter_username(user.username)
    login_page.enter_password(user.password)
    login_page.click_login()
    time.sleep(2)
    OTPPage().enter_otp('ataiyr', OTPPage.otp)
