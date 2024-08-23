from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePageWithWait(BasePage):
    def wait_for_elements_to_load(self, locators, timeout=10):
        for locator in locators:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

class Visa_AFT(BasePageWithWait):
    bank_account_parent_layout_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/bank_account_parent_layout")
    select_bank_account_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/bank_account_view")
    card_number_input_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardField")
    full_name_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/userNameField")
    expiry_date_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardExpiryField")
    security_code_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cvc")
    amound_to_transfer_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/amount_et")
    submit_button_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/button_frame_layout")

    def wait_for_page_to_load(self):
        locators = [
            self.bank_account_parent_layout_AFT,
            self.select_bank_account_AFT,
            self.card_number_input_AFT,
            self.full_name_AFT,
            self.expiry_date_AFT,
            self.security_code_AFT,
            self.amound_to_transfer_AFT,
            self.submit_button_AFT
        ]
        self.wait_for_elements_to_load(locators)
