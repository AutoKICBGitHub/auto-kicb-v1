from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePageWithWait(BasePage):
    def wait_for_elements_to_load(self, locators, timeout=10):
        for locator in locators:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

class LoginPage(BasePageWithWait):
    username_field = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/login_et")
    password_field = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/password_et")
    login_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/auth_progress_button")

    def enter_username(self, username):
        self.send_keys(self.username_field, username)

    def enter_password(self, password):
        self.send_keys(self.password_field, password)

    def click_login(self):
        self.click(self.login_button)

    def wait_for_page_to_load(self):
        locators = [
            self.username_field,
            self.password_field,
            self.login_button
        ]
        self.wait_for_elements_to_load(locators)

class FooterMainPage(BasePageWithWait):
    accounts_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_account")
    payments_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_payments")
    qr_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_qr")
    services_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_showcase")
    history_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_history")

    def wait_for_page_to_load(self):
        locators = [
            self.accounts_button,
            self.payments_button,
            self.qr_button,
            self.services_button,
            self.history_button
        ]
        self.wait_for_elements_to_load(locators)
