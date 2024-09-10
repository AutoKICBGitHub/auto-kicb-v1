class PaymentsPage:
    def __init__(self, page):
        self.page = page

    def select_account(self, account_index):
        self.page.locator("//div[@class='popup-select']").nth(account_index).wait_for(timeout=60000)
        self.page.locator("//div[@class='popup-select']").nth(account_index).click()

    def select_currency(self, currency_index):
        self.page.locator("//div[@class='popup-select']//li").nth(currency_index).wait_for(timeout=10000)
        self.page.locator("//div[@class='popup-select']//li").nth(currency_index).click()

    def enter_amount(self, amount):
        self.page.locator("//div[@class='exchange-fields']//label").nth(0).fill(str(amount))

    def confirm_payment(self):
        self.page.locator("//div[@class='transfer-own__button']//button").is_visible(timeout=10000)
        self.page.locator("//div[@class='transfer-own__button']//button").click()
