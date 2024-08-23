from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class Visa_AFT(BasePage):
    bank_account_parent_layout_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/bank_account_parent_layout")
    select_bank_account_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/bank_account_view")
    card_number_input_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardField")
    full_name_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/userNameField")
    expiry_date_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cardExpiryField")
    security_code_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/cvc")
    amound_to_transfer_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/amount_et")
    submit_button_AFT = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/button_frame_layout")
