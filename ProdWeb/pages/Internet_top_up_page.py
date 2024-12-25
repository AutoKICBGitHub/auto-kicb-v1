from playwright.sync_api import Page
from pages.Base_page import BasePage
from time import sleep

class Intenet_and_tv_top_up_Page(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_button = "//a [@href='/payment']"
        self.internet_and_tv_button = "//a [@href='/payment/provider?id=481']"
        self.internet_button = "//div [contains(text(), 'Интернет')]"
        
        self.Aknet_button = "//div [contains(text(), 'Aknet')]"
        self.account_locator = "//p [contains(text(), 'Счет списания')]//..//div"
        self.account_locator_som = "//p [contains(text(), '1280016059196988')]"
        self.generic_payment_input = "//input [@class='generic-payment__input']"
        self.amount_to_top_up = "//input [@type = 'text']"
        self.top_up_pay_button = "//button [contains(text(), 'Оплатить')]"
        self.payment_top_up_conf_button = "//button [contains(text(), 'Отправить на подтверждение')]"
        self.goto_main_page = "//a [@href='/']"


    def intenet_top_up_aknet (self):
        self.page.click(self.payment_button)
        self.page.click(self.internet_and_tv_button)
        self.page.locator(self.internet_button).nth(0).wait_for(timeout=9000)
        self.page.locator(self.internet_button).nth(0).click()
        self.page.locator(self.Aknet_button).nth(0).wait_for(timeout=9000)
        self.page.locator(self.Aknet_button).nth(0).click()
        self.page.locator(self.account_locator).nth(1).click()
        self.page.locator(self.account_locator_som).click()
        self.page.locator(self.generic_payment_input).fill("3445602")
        self.page.locator(self.amount_to_top_up).fill("10")
        if self.page.locator(self.top_up_pay_button).is_visible(timeout=5000):
            self.page.locator(self.top_up_pay_button).click()
        else: 
            print("Ошибка кнопка Перевести не найдена")     
        self.page.locator(self.payment_top_up_conf_button).wait_for(timeout=5000)
        if self.page.locator(self.payment_top_up_conf_button).is_visible(timeout=5000):
            self.page.locator(self.payment_top_up_conf_button).click()
        else: 
            print("Ошибка кнопка подтвердить не найдена")    
        self.page.locator(self.goto_main_page).nth(0).click()
