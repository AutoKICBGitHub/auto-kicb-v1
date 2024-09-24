import pytest
import time
import logging
from playwright.sync_api import Playwright
from Web_auto_dev.Pages.Login import LoginPage
from Web_auto_dev.Pages.OTP import OTPPage
from Web_auto_dev.Pages.Payment import PaymentsPage
from Web_auto_dev.Other.transfer_accounts import accounts  # Загружаем аккаунты для теста

# Путь к файлу для сохранения успешных аккаунтов
SUCCESSFUL_ACCOUNTS_FILE = 'transfer_accounts1.py'

# Попытка загрузить успешные аккаунты
try:
    with open(SUCCESSFUL_ACCOUNTS_FILE, 'r') as f:
        exec(f.read())
except (FileNotFoundError, SyntaxError):
    successful_accounts = []  # Если файл не найден или пуст, создаем пустой список

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


@pytest.mark.parametrize("account", accounts)
def test_transaction_between_accounts(browser_context, account):
    page = browser_context.new_page()
    page.goto("https://newibanktest.kicb.net/login")

    # Инициализация страниц
    login_page = LoginPage(page)
    otp_page = OTPPage(page)
    payments_page = PaymentsPage(page)

    # Выполняем вход
    login_page.login_in_system('aigerimk')

    try:
        otp_page.login_in_system('aigerimk')
    except Exception as e:
        logger.error(f"Ошибка при вводе OTP: {e}")

    try:
        # Проверяем наличие сообщения "Неизвестная ошибка!"
        if page.locator("//span [@class='confirm-otp__error']").is_visible():
            logger.warning("Обнаружена 'Неизвестная ошибка!'. Повторный ввод OTP.")
            otp_field = page.locator("//input[@type='password']")
            otp_field.fill('')  # Очищаем поле перед повторным вводом
            otp_page.login_in_system('aigerimk')  # Повторяем ввод OTP
    except Exception as e:
        logger.error(f"Ошибка при повторном вводе OTP: {e}")

    # try:
    #     page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
    #     logger.info("Карты успешно загружены.")
    # except:
    #     logger.error("Карты не удалось загрузить после нескольких попыток.")
    #     page.reload()
    time.sleep(6)
    # Открываем раздел Платежи
    payments_page.open_payments()
    page.locator("//p[contains(@class, 'operation-card__text') and contains(text(), 'Клиенту KICB')]").wait_for(timeout=30000)
    page.locator("//p[contains(@class, 'operation-card__text') and contains(text(), 'Клиенту KICB')]").click()

    # Переходим к карте
    page.locator("//div[@class='card-wrapper__item']").wait_for(timeout=30000)
    page.locator("//div[@class='card-wrapper__item']").click()

    # Используем текущий аккаунт из параметризации
    target_account = account['account_no']  # Выбираем аккаунт для перевода
    page.locator("//p[contains(text(), '1285000000301116')]").wait_for(timeout=30000)
    page.locator("//p[contains(text(), '1285000000301116')]").click()

    # Заполняем сумму и аккаунт
    page.locator("//input[@class='custom-input__field custom-input__text']").wait_for(timeout=30000)
    page.locator("//input[@class='custom-input__field custom-input__text']").fill(target_account)
    page.locator("//input[@class='q-field__native q-placeholder custom-input__text']").nth(1).fill('5.03')
    page.locator("//button[@class='custom-button custom-button--active']").wait_for(timeout=30000)
    page.locator("//button[@class='custom-button custom-button--active']").click()

    # Проверка на ошибку счета
    try:
        # Явное ожидание появления ошибки на странице с таймаутом
        if page.wait_for_selector("//span[contains(text(), 'Счет')]", timeout=10000):
            logger.warning(f"Проблема с аккаунтом {target_account}.")
        else:
            logger.info("Ошибки не обнаружено, добавляем аккаунт в успешные.")


    except Exception as e:
        logger.error(f"Ошибка при проверке наличия ошибки счета: {e}")
        try:
            # Явное ожидание появления ошибки на странице с таймаутом
            if page.wait_for_selector("//span[contains(text(), 'Внутренняя')]", timeout=3000):
                successful_accounts.append({"account_internal": target_account})
            else:
                logger.info("Ошибки не обнаружено, добавляем аккаунт в успешные.")

        except Exception as e:
            page.locator("//button[@class='custom-button custom-button--accept custom-button--active']").wait_for(
                timeout=30000)
            page.locator("//button[@class='custom-button custom-button--accept custom-button--active']").click()

            # Вводим OTP для подтверждения
            otp_page.login_in_system('aigerimk')
            time.sleep(3)
            # Переходим на следующую страницу
            page.locator("//a[@class='header-nav__link']").nth(1).wait_for(timeout=30000)
            page.locator("//a[@class='header-nav__link']").nth(1).click()
            successful_accounts.append({"account_no": target_account})  # Добавляем аккаунт в массив успешных записей
            time.sleep(1)  # Задержка для проверки результатов вручную

            # Сохраняем успешные аккаунты в файл
            with open(SUCCESSFUL_ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
                f.write('successful_accounts = [\n')
                for account in successful_accounts:
                    f.write(f'    {account},\n')
                f.write(']\n')
    # Закрываем браузер
    browser_context.close()
