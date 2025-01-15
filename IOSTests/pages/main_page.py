from .base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy


class MainPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # Табы навигации
        self.home_tab = '//XCUIElementTypeButton[@name="Счета"]'
        self.payments_tab = '//XCUIElementTypeButton[@name="Платежи"]'
        self.qr_tab = '//XCUIElementTypeButton[@name="KICB QR"]'
        self.services_tab = '//XCUIElementTypeButton[@name="Сервисы"]'
        self.history_tab = '//XCUIElementTypeButton[@name="История"]'
        
        # Элементы главного экрана
        self.user_name = '//XCUIElementTypeStaticText[@name="Ырысбеков Атай Айбекович"]'
        self.client_code = '//XCUIElementTypeStaticText[contains(@name, "Код клиента:")]'
        self.accounts_title = '//XCUIElementTypeStaticText[@name="Карты и счета"]'
    
    def is_main_page_displayed(self):
        """Проверка, что мы на главной странице"""
        return self.wait_for_element_to_be_visible(self.user_name)
    
    def go_to_payments(self):
        """Переход на страницу платежей"""
        self.click_element(self.payments_tab)
        print("✅ Выполнен переход на страницу платежей")
    
    def go_to_services(self):
        """Переход на страницу сервисов"""
        self.click_element(self.services_tab)
    
    def go_to_history(self):
        """Переход на страницу истории"""
        self.click_element(self.history_tab)
    
    def go_to_qr(self):
        """Переход на страницу QR"""
        self.click_element(self.qr_tab)
    
    def go_to_home(self):
        """Переход на главную страницу"""
        self.click_element(self.home_tab)
    
    
