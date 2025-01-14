from .base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy


class LoginPage(BasePage):
    # Локаторы
    username_field = (AppiumBy.ACCESSIBILITY_ID, "username_input")
    password_field = (AppiumBy.ACCESSIBILITY_ID, "password_input")
    login_button = (AppiumBy.ACCESSIBILITY_ID, "login_button")
    error_message = (AppiumBy.ACCESSIBILITY_ID, "error_message")

    def enter_username(self, username):
        self.send_keys(self.username_field, username)

    def enter_password(self, password):
        self.send_keys(self.password_field, password)

    def tap_login_button(self):
        self.click(self.login_button)

    def is_error_visible(self):
        return self.is_element_visible(self.error_message)
