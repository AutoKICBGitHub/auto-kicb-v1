from playwright.sync_api import Page
from pages.Base_page import BasePage
from time import sleep

class ExchangePage1(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_button = "//a [@href='/payment']"
        self.exchange_button = "//a [@href='/payment/exchange']"
        self.account_locator = "//p [contains(text(), 'Счет списания')]//..//div"
        self.account_locator_som = "//p [contains(text(), '1280016059196988')]"
        self.account_locator_2 = "//p [contains(text(), 'Счет пополнения')]//..//div"
        self.account_locator_dollar = "//p [contains(text(), '1285330003310291')]"
        self.amount_debit = "//p [contains(text(), 'Сумма к списанию')]//..//div"
        self.exchange_button_accept = "//button [contains(text(), 'Обменять')]"
        self.exchange_button_confirm = "//button [contains(text(), 'Подтвердить')]"





    def exchange_1 (self):
        """Выполняет запрос на обмен валюты"""
        self.page.click(self.payment_button)
        self.page.locator(self.exchange_button).nth(0).click()
        self.page.locator(self.account_locator).nth(1).click()
        self.page.locator(self.account_locator_som).click()
        self.page.locator(self.account_locator_2).nth(1).click()
        self.page.locator(self.account_locator_dollar).click()
        self.page.locator(self.amount_debit).nth(1).fill("10")
        self.page.locator(self.exchange_button_accept).click()
        self.page.locator(self.exchange_button_confirm).click()




 





    
