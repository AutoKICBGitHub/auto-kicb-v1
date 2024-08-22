import pytest
import time
from AndroidTests.pages.login_page import LoginPage
from AndroidTests.pages.otp_page import OTPPage
# from AndroidTests.pages.home_page import HomePage
from AndroidTests.utils.adb_utils import ADBUtils_otp
from AndroidTests.utils.adb_utils import ADBUtils_coords
from AndroidTests.users import get_user


@pytest.fixture()
def driver(appium_driver):
    return appium_driver

class login_user_3_steps:
    def test_login(driver):
        user = get_user('1')
        login_page = LoginPage(driver)
        # home_page = HomePage(driver)
        login_page.enter_username(user.username)
        login_page.enter_password(user.password)
        login_page.click_login()
        time.sleep(2)

    def test_otp_page(driver):
        user = get_user('1')
        ADBUtils_otp.enter_otp_via_adb(user.otp)
        time.sleep(1)

    def test_phone_password(driver):
        x = 106
        y = 2240
        z = 750
        c = 1100
        ADBUtils_coords.click_by_coordinates(ADBUtils_coords.click_by_coordinates, x, y)
        ADBUtils_coords.enter_pin_code_via_adb(ADBUtils_coords.enter_pin_code_via_adb, "3385")
        ADBUtils_coords.click_by_coordinates(ADBUtils_coords.click_by_coordinates, z, c)



def test_login_init(driver):
    login_user_3_steps.test_login(driver)
    login_user_3_steps.test_otp_page(driver)
    login_user_3_steps.test_phone_password(driver)



