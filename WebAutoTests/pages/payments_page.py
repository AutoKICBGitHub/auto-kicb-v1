import time

class PaymentsPage:
    def __init__(self, page):
        self.page = page
    def open_payments(self):
        self.page.locator("//a [@href='/payment']").wait_for(timeout=60000)
        self.page.locator("//a [@href='/payment']").click()

    def open_exchange(self):
        self.page.locator("p.operation-card__text:has-text('Обмен валют')").wait_for(timeout=60000)
        self.page.locator("p.operation-card__text:has-text('Обмен валют')").click()

    def exchange_usd_kgs(self):
        self.page.locator("//div [@class='popup-select']").nth(0).wait_for(timeout=60000)
        self.page.locator("//div [@class='popup-select']").nth(0).click()
        # Выбор счета в долларах
        self.page.locator("//div [@class='popup-select'] //li").nth(6).wait_for(timeout=10000)
        self.page.locator("//div [@class='popup-select'] //li").nth(6).click()

        # Выбор счета 2
        self.page.locator("//div [@class='popup-select']").nth(1).wait_for(timeout=60000)
        self.page.locator("//div [@class='popup-select']").nth(1).click()
        # Выбор счета в сомах
        self.page.locator("//div [@class='popup-select'] //li").nth(5).wait_for(timeout=10000)
        self.page.locator("//div [@class='popup-select'] //li").nth(5).click()

        self.page.locator("//div [@class='exchange-fields'] //label").nth(0).fill("1")
        self.page.locator("//div [@class='transfer-own__button'] //button").is_visible(timeout=10000)
        self.page.locator("//div [@class='transfer-own__button'] //button").click()

        time.sleep(1)

        self.page.locator("//button [@class='custom-button custom-button--active']").wait_for(timeout=10000)
        self.page.locator("//button [@class='custom-button custom-button--active']").click()


