import logging
import time
from webTest.Web_test_page_object.pages.login_page import LoginPage
from webTest.Web_test_page_object.pages.otp_page import OtpPage
from webTest.Web_test_page_object.pages.payments_page import PaymentsPage
from webTest.Web_test_page_object.utils.users import get_user

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_currency_exchange(playwright):
    # Get the first user data
    user = get_user('1')
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Инициализация страниц
    login_page = LoginPage(page)
    otp_page = OtpPage(page)
    payments_page = PaymentsPage(page)

    # Login flow
    logger.info("Переход на страницу входа")
    login_page.navigate()
    logger.info("Заполнение учетных данных")
    login_page.login(user['username'], user['password'])

    # OTP flow
    logger.info("Ввод OTP")
    otp_page.enter_otp(user['otp_secret'])

    # Проверка загрузки карт
    try:
        page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
        logger.info("Карты успешно загружены.")
    except:
        logger.error("Карты не удалось загрузить после нескольких попыток.")
        page.reload()

    # Payments flow
    logger.info("Переход в раздел платежей")
    page.locator("//nav[@class='header-nav']//a").nth(1).wait_for(timeout=60000)
    page.locator("//nav[@class='header-nav']//a").nth(1).click()

    logger.info("Выбор счета для обмена валют")
    payments_page.select_account(0)  # Выбираем первый счет
    payments_page.select_currency(6)  # Выбираем доллар
    payments_page.select_account(1)  # Выбираем второй счет
    payments_page.select_currency(5)  # Выбираем сомы

    logger.info("Ввод суммы и подтверждение обмена")
    payments_page.enter_amount(1)
    payments_page.confirm_payment()

    # Завершение работы и закрытие браузера
    logger.info("Завершение теста и закрытие браузера")
    context.close()
    browser.close()
