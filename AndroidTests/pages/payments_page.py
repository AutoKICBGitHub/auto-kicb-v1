from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePageWithWait(BasePage):
    def wait_for_elements_to_load(self, locators, timeout=10):
        for locator in locators:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

class PaymentsTopUp(BasePageWithWait):
    ELQR_top_up_button = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[1]")
    Visa_top_up_button = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[2]")

    def wait_for_page_to_load(self):
        locators = [
            self.ELQR_top_up_button,
            self.Visa_top_up_button
        ]
        self.wait_for_elements_to_load(locators)

class TransfersKICB(BasePageWithWait):
    between_accounts_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[3]")
    money_exchange_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[4]")
    KICB_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[5]")
    clearing_gross_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[6]")
    SWIFT_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[7]")
    card_nonKICB_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[8]")

    def wait_for_page_to_load(self):
        locators = [
            self.between_accounts_transfer,
            self.money_exchange_transfer,
            self.KICB_transfer,
            self.clearing_gross_transfer,
            self.SWIFT_transfer,
            self.card_nonKICB_transfer
        ]
        self.wait_for_elements_to_load(locators)

class PaymentsKICB(BasePageWithWait):
    salyk_taxes_payment = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[2]")

    def wait_for_page_to_load(self):
        locators = [
            self.salyk_taxes_payment
        ]
        self.wait_for_elements_to_load(locators)
