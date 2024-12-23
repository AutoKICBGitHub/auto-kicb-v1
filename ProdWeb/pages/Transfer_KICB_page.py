from playwright.sync_api import Page
from pages.Base_page import BasePage
from time import sleep

class Transfer_KICB_page1(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.payment_button = "//a [@href='/payment']"
        self.to_KICB_client = "//a [@href='/payment/other-accounts']"
        self.account_locator = "//p [contains(text(), 'Счет списания')]//..//div"
        self.account_locator_som = "//p [contains(text(), '1280016059196988')]"
        self.account_locator_account = "//p [contains(text(), 'Счет получателя')]//..//input"
        self.account_locator_card = "//p [contains(text(), 'Номер карты')]//..//input"
        self.account_locator_phone_nubmer = "//p [contains(text(), 'Номер телефона')]//..//input"
        self.transaction_type_account = "//button [contains(text(), 'Счет')]"
        self.transaction_type_card = "//button [contains(text(), 'Карта')]"
        self.transaction_type_phone_nubmer = "//button [contains(text(), 'Телефон')]"
        self.transfer_amount = "//p [contains(text(), 'Сумма перевода')]//..//input"
        self.transaction_button_transfer = "//button [contains(text(), 'Перевести')]"
        self.transaction_button_confirm = "//button [contains(text(), 'Подтвердить')]"
        self.goto_main_page = "//a [@href='/']"





    def Transfer_KICB_card (self):
        self.page.click(self.payment_button)
        self.page.locator(self.to_KICB_client).nth(0).click()
        self.page.locator(self.account_locator).nth(1).click()
        self.page.locator(self.account_locator_som).click()
        self.page.locator(self.transaction_type_card).wait_for(timeout=5000)
        self.page.locator(self.transaction_type_card).click()
        self.page.locator(self.account_locator_card).wait_for(timeout=5000)
        self.page.locator(self.account_locator_card).fill("4446791000018356")
        self.page.locator(self.transfer_amount).fill("1")
        self.page.locator(self.transaction_button_transfer).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_transfer).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_transfer).click()
        else: 
            print("Ошибка кнопка Перевести не найдена")     
        self.page.locator(self.transaction_button_confirm).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_confirm).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_confirm).click()
        else: 
            print("Ошибка кнопка подтвердить не найдена")    
        self.page.locator(self.goto_main_page).nth(0).click()

    
    def Transfer_KICB_account (self):    
        self.page.click(self.payment_button)
        self.page.locator(self.to_KICB_client).nth(0).click()
        self.page.locator(self.account_locator).nth(1).click()
        self.page.locator(self.account_locator_som).click()
        self.page.locator(self.transaction_type_account).wait_for(timeout=5000)
        self.page.locator(self.transaction_type_account).click()
        self.page.locator(self.account_locator_account).wait_for(timeout=5000)
        self.page.locator(self.account_locator_account).fill("1280016057421282")
        self.page.locator(self.transfer_amount).fill("1")
        self.page.locator(self.transaction_button_transfer).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_transfer).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_transfer).click()
        else: 
            print("Ошибка кнопка Перевести не найдена")     
        self.page.locator(self.transaction_button_confirm).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_confirm).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_confirm).click()
        else: 
            print("Ошибка кнопка подтвердить не найдена")    
        self.page.locator(self.goto_main_page).nth(0).click()
    def Transfer_KICB_phone_nubmer (self):    
        self.page.click(self.payment_button)
        self.page.locator(self.to_KICB_client).nth(0).click()
        self.page.locator(self.account_locator).nth(1).click()
        self.page.locator(self.account_locator_som).click()
        self.page.locator(self.transaction_type_phone_nubmer).wait_for(timeout=5000)
        self.page.locator(self.transaction_type_phone_nubmer).click()
        self.page.locator(self.account_locator_phone_nubmer).wait_for(timeout=5000)
        self.page.locator(self.account_locator_phone_nubmer).fill("555515516")
        self.page.locator(self.transfer_amount).fill("1")
        self.page.locator(self.transaction_button_transfer).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_transfer).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_transfer).click()
        else: 
            print("Ошибка кнопка Перевести не найдена")     
        self.page.locator(self.transaction_button_confirm).wait_for(timeout=5000)
        if self.page.locator(self.transaction_button_confirm).is_visible(timeout=5000):
            self.page.locator(self.transaction_button_confirm).click()
        else: 
            print("Ошибка кнопка подтвердить не найдена")    
        self.page.locator(self.goto_main_page).nth(0).click()




    
