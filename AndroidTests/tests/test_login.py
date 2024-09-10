import pytest
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from AndroidTests.pages.login_page import LoginPage, FooterMainPage
from AndroidTests.pages.payments_page import PaymentsTopUp
from AndroidTests.utils.adb_utils import ADBUtils
from AndroidTests.users import get_user
from AndroidTests.pages.Visa_AFT import Visa_AFT
from AndroidTests.Visa_card_info import get_visa_card

@pytest.fixture()
def driver(appium_driver):
    return appium_driver

class LoginUser3Steps:
    def test_login(self, driver):
        user = get_user('3')
        login_page = LoginPage(driver)
        login_page.wait_for_page_to_load()  # Ожидание загрузки страницы логина
        login_page.enter_username(user.username)
        login_page.enter_password(user.password)
        login_page.click_login()
        time.sleep(2)

    def test_otp_page(self, driver):
        user = get_user('3')
        ADBUtils.enter_otp_via_adb(user.otp)
        time.sleep(1)

    def test_phone_password(self, driver):
        ADBUtils.click_by_coordinates(106, 2240)
        ADBUtils.enter_pin_code_via_adb("3385")
        # ADBUtils.click_by_coordinates(750, 1100)
        ADBUtils.click_by_coordinates(1250, 2750)


class test_enter_visa_details:
    def go_to_payments(self, driver):
        WebDriverWait(self, 40).until(
            EC.presence_of_element_located((AppiumBy.XPATH,
                                            '(//android.widget.RelativeLayout[@resource-id="net.kicb.ibankprod.dev:id/bank_account_view"])[5]'))
        )

        footer = FooterMainPage(self)
        footer.click(footer.payments_button)
    def top_up_visa_details(self, driver):
        top_up = PaymentsTopUp(driver)
        top_up.click(top_up.Visa_top_up_button)
        card = get_visa_card('1')
        AFT = Visa_AFT(driver)

        AFT.click(AFT.bank_account_parent_layout_AFT)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(AFT.select_bank_account_AFT)
        )
        AFT.click(AFT.select_bank_account_AFT)
        AFT.send_keys(AFT.card_number_input_AFT, card.card_number)
        AFT.send_keys(AFT.full_name_AFT, card.full_name)
        AFT.send_keys(AFT.expiry_date_AFT, card.expiry_date)
        AFT.send_keys(AFT.security_code_AFT, card.security_code)
        AFT.send_keys(AFT.amound_to_transfer_AFT, card.amount_to_transfer)
        driver.hide_keyboard()
        AFT.click(AFT.submit_button_AFT)
        time.sleep(10)


def test_login_init(driver):
    steps = LoginUser3Steps()
    steps.test_login(driver)
    steps.test_otp_page(driver)
    steps.test_phone_password(driver)
    test_enter_visa_details.go_to_payments(driver)
    test_enter_visa_details.top_up_visa_details(driver)

