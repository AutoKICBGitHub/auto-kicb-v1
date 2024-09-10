import logging
import playwright
from WebAutoTests.pages.login_page import LoginPage
from WebAutoTests.pages.otp_page import OtpPage
from WebAutoTests.pages.payments_page import PaymentsPage
from WebAutoTests.utils.users import get_user

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginAutomation:
    def __init__(self, playwright):
        self.playwright = playwright
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def login_user(self, user):
        # Инициализация страниц
        login_page = LoginPage(self.page)
        otp_page = OtpPage(self.page)

        # Login flow
        logger.info("Переход на страницу входа")
        login_page.navigate()
        logger.info("Заполнение учетных данных")
        login_page.login(user.username, user.password)

        # OTP flow
        logger.info("Ввод OTP")
        otp_page.enter_otp(user.otp_secret)

        # Проверка загрузки карт
        try:
            self.page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
            logger.info("Карты успешно загружены.")
        except:
            logger.error("Карты не удалось загрузить после нескольких попыток.")
            self.page.reload()

class PaymentExchangeUsdKgs(PaymentsPage):
    def __init__(self, page):
        super().__init__(page)

    def perform_exchange(self):
        self.open_payments()
        self.open_exchange()
        self.exchange_usd_kgs()


def close(self):
    self.context.close()
    self.browser.close()
