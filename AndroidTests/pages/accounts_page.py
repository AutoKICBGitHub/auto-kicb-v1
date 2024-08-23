from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePageWithWait(BasePage):
    def wait_for_elements_to_load(self, locators, timeout=10):
        for locator in locators:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

class HeaderMainPage(BasePageWithWait):
    profile_avatar_settings = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/profile_avatar_iv")
    notifications_small_icon = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/notifications_iv")
    messages_small_icon = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/messages_iv")

    def wait_for_page_to_load(self):
        locators = [
            self.profile_avatar_settings,
            self.notifications_small_icon,
            self.messages_small_icon
        ]
        self.wait_for_elements_to_load(locators)

class BodyMainPageCards(BasePageWithWait):
    bank_accounts_list_1 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[1]"
    )
    bank_accounts_list_2 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[2]"
    )
    bank_accounts_list_3 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[3]"
    )
    bank_accounts_list_4 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[4]"
    )
    bank_accounts_list_5 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[5]"
    )
    bank_accounts_list_6 = (
        AppiumBy.XPATH,
        "(//android.widget.RelativeLayout[@resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[6]"
    )

    def wait_for_page_to_load(self):
        locators = [
            self.bank_accounts_list_1,
            self.bank_accounts_list_2,
            self.bank_accounts_list_3,
            self.bank_accounts_list_4,
            self.bank_accounts_list_5,
            self.bank_accounts_list_6
        ]
        self.wait_for_elements_to_load(locators)

class BodyMainPageTemplates(BasePageWithWait):
    templates_list_1 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[1]"
    )
    templates_list_2 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[2]"
    )
    templates_list_3 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[3]"
    )
    templates_list_4 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[4]"
    )
    templates_list_5 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[5]"
    )
    templates_list_6 = (
        AppiumBy.XPATH,
        "(//androidx.recyclerview.widget.RecyclerView[@resource-id='net.kicb.ibankprod.dev:id/assets_rv'])[2]/android.widget.LinearLayout[6]"
    )

    def wait_for_page_to_load(self):
        locators = [
            self.templates_list_1,
            self.templates_list_2,
            self.templates_list_3,
            self.templates_list_4,
            self.templates_list_5,
            self.templates_list_6
        ]
        self.wait_for_elements_to_load(locators)
