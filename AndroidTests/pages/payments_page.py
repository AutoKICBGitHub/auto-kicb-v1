from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class payments_top_up(BasePage):
    ELQR_top_up_button = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[1]")
    Visa_top_up_button = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[2]")

class transfers_kicb(BasePage):
    between_accounts_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[3]")
    money_exchange_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[4]")
    KICB_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[5]")
    clearing_gross_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[6]")
    SWIFT_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[7]")
    Card_nonKICB_transfer = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[8]")
class payments_kicb(BasePage):
    salyk_taxes_payment = (AppiumBy.XPATH, "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/parentView'])[2]")