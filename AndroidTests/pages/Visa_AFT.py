from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from AndroidTests.pages.login_page import footer_main_page
from AndroidTests.pages.payments_page import payments_top_up


class Visa_AFT(BasePage):
    bank_account_parent_layout_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/bank_account_parent_layout")
    card_number_input_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardField")
    full_name_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/userNameField")
    expiry_date_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardExpiryField")
    security_code_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cvc")
    amound_to_transfer_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/amount_et")
    submit_button_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/button_frame_layout")




    def test1(self):
        self.click(footer_main_page.payments_button)

    def test2(self):
        self.click(payments_top_up.Visa_top_up_button)