from .base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_field = "username_input"
        self.password_field = "password_input"
        self.login_button = "login_button"
        self.success_message = "success_message"
    
    def enter_username(self, username):
        self.find_element_by_accessibility_id(self.username_field).send_keys(username)
    
    def enter_password(self, password):
        self.find_element_by_accessibility_id(self.password_field).send_keys(password)
    
    def tap_login_button(self):
        self.find_element_by_accessibility_id(self.login_button).click()
    
    def is_success_message_displayed(self):
        return self.find_element_by_accessibility_id(self.success_message).is_displayed()
