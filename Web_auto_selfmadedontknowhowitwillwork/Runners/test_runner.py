import pytest
import time
import logging
from playwright.sync_api import Playwright
from Web_auto_selfmadedontknowhowitwillwork.Pages.Login import LoginPage
from Web_auto_selfmadedontknowhowitwillwork.Pages.OTP import OTPPage
from Web_auto_selfmadedontknowhowitwillwork.Pages.Payment import PaymentsPage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def browser_context(playwright: Playwright):
    # Создаем браузерный контекст для теста
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    yield context
    context.close()
    browser.close()

def test_exchange(browser_context):
    page = browser_context.new_page()
    page.goto("https://ibank.kicb.net/login")

    # Инициализация страниц
    login_page = LoginPage(page)
    otp_page = OTPPage(page)
    payments_page = PaymentsPage(page)
    # Выполняем вход
    login_page.login_in_system('ataiy')
    try:
        otp_page.login_in_system('ataiy')
    except Exception as e:
        logger.error(f"Ошибка при вводе OTP: {e}")

    try:
        # Проверяем наличие сообщения "Неизвестная ошибка!"
        if page.locator("//span [@class='confirm-otp__error']").is_visible():
            logger.warning("Обнаружена 'Неизвестная ошибка!'. Повторный ввод OTP.")
            # Удаляем предыдущий код с помощью backspace

            for _ in range(6):  # Нажимаем backspace 6 раз для очистки всех полей
                page.keyboard.press('Backspace')
                time.sleep(5)
            otp_page.login_in_system('ataiy')  # Повторяем ввод OTP
    except Exception as e:
        logger.error(f"Ошибка при повторном вводе OTP: {e}")

    try:
        page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
        logger.info("Карты успешно загружены.")
    except:
        logger.error("Карты не удалось загрузить после нескольких попыток.")
        page.reload()

    # Открываем раздел Платежи
    payments_page.open_payments()
    payments_page.open_exchange()
    payments_page.exchange_usd_kgs()
    payments_page.open_payments()
    payments_page.open_exchange()
    payments_page.exchange_kgs_usd()
    # Закрываем браузер
    browser_context.close()

def test_transaction_between_accounts(browser_context):
    page = browser_context.new_page()
    page.goto("https://ibank.kicb.net/login")

    # Инициализация страниц
    login_page = LoginPage(page)
    otp_page = OTPPage(page)
    payments_page = PaymentsPage(page)
    # Выполняем вход
    login_page.login_in_system('ataiy')
    try:
        otp_page.login_in_system('ataiy')
    except Exception as e:
        logger.error(f"Ошибка при вводе OTP: {e}")

    try:
        # Проверяем наличие сообщения "Неизвестная ошибка!"
        if page.locator("//span [@class='confirm-otp__error']").is_visible():
            logger.warning("Обнаружена 'Неизвестная ошибка!'. Повторный ввод OTP.")
            # Удаляем предыдущий код с помощью backspace

            for _ in range(6):  # Нажимаем backspace 6 раз для очистки всех полей
                page.keyboard.press('Backspace')
                time.sleep(5)
            otp_page.login_in_system('ataiy')  # Повторяем ввод OTP
    except Exception as e:
        logger.error(f"Ошибка при повторном вводе OTP: {e}")

    try:
        page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
        logger.info("Карты успешно загружены.")
    except:
        logger.error("Карты не удалось загрузить после нескольких попыток.")
        page.reload()

    # Открываем раздел Платежи
    payments_page.open_payments()
    payments_page.open_transaction_between_accounts()
    payments_page.transaction_between_accounts_1_2()
    payments_page.open_payments()
    payments_page.open_transaction_between_accounts()
    payments_page.transaction_between_accounts_2_1()
    # Закрываем браузер
    browser_context.close()
