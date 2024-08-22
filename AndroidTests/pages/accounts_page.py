from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class header_main_page(BasePage):
    profile_avatar_settings = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/profile_avatar_iv")
    notifications_small_icon = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/notifications_iv")
    messages_small_icon = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/messages_iv")

class body_main_page_cards(BasePage):
    bank_accounts_list_1 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[1]"
    )
    bank_accounts_list_2 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[2]"
    )
    bank_accounts_list_3 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[3]"
    )
    bank_accounts_list_4 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[4]"
    )
    bank_accounts_list_5 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[5]"
    )
    bank_accounts_list_6 = (
        AppiumBy.XPATH,
        "(// android.widget.RelativeLayout[@ resource-id='net.kicb.ibankprod.dev:id/bank_account_view'])[6]"
    )

class BodyMainPageTemplates(BasePage):
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

