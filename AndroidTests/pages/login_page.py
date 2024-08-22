from AndroidTests.utils.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class LoginPage(BasePage):
    username_field = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/login_et")
    password_field = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/password_et")
    login_button = (AppiumBy.ID, "net.kicb.ibankprod.dev:id/auth_progress_button")

    def enter_username(self, username):
        self.send_keys(self.username_field, username)

    def enter_password(self, password):
        self.send_keys(self.password_field, password)

    def click_login(self):
        self.click(self.login_button)


