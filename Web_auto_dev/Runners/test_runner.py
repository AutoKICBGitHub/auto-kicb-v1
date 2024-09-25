import pytest
import time
import logging
import random
from datetime import datetime, timedelta
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
    browser = playwright.chromium.launch(headless=True)
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
    login_page.login_in_system('1')

    try:
        otp_page.login_in_system('1')
    except Exception as e:
        logger.error(f"Ошибка при вводе OTP: {e}")

    try:
        # Проверяем наличие сообщения "Неизвестная ошибка!"
        if page.locator("//span [@class='confirm-otp__error']").is_visible():
            logger.warning("Обнаружена 'Неизвестная ошибка!'. Повторный ввод OTP.")
            otp_field = page.locator("//input[@type='password']")
            otp_field.fill('')  # Очищаем поле перед повторным вводом
            otp_page.login_in_system('1')  # Повторяем ввод OTP
    except Exception as e:
        logger.error(f"Ошибка при повторном вводе OTP: {e}")

    # try:
    #     page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
    #     logger.info("Карты успешно загружены.")
    # except:
    #     logger.error("Карты не удалось загрузить после нескольких попыток.")
    #     page.reload()
    time.sleep(20)
    # Открываем раздел Платежи
    payments_page.open_payments()
    page.locator("//a [@href='/payment/other-accounts']").wait_for(timeout=30000)
    page.locator("//p[contains(@class, 'operation-card__text') and contains(text(), 'Клиенту KICB')]").click()

    # Переходим к карте
    page.locator("//div[@class='card-wrapper__item']").wait_for(timeout=30000)
    page.locator("//div[@class='card-wrapper__item']").click()

    # Используем текущий аккаунт из параметризации
    target_account = account['account_no']  # Выбираем аккаунт для перевода
    page.locator("//p[contains(text(), '4446 **** **** 6359')]").nth(0).wait_for(timeout=30000)
    page.locator("//p[contains(text(), '4446 **** **** 6359')]").nth(0).click()
    if page.locator("//p [contains(text(), 'Документа')]").is_visible():
        random_value = str(random.randint(1000, 9999))
        page.locator("//p [contains(text(), 'Документа')] //..//label").wait_for(timeout=30000)
        page.locator("//p [contains(text(), 'Документа')] //..//label").fill(random_value)
        page.locator("//p [contains(text(), 'Код платежа')] //..//label").wait_for(timeout=30000)
        page.locator("//p [contains(text(), 'Код платежа')] //..//label").fill("55609000")
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')
        page.locator("//p [contains(text(), 'Дата валютирования')] //..//input").wait_for(timeout=30000)
        page.locator("//p [contains(text(), 'Дата валютирования')] //..//input").fill(tomorrow_date)
        page.locator("//p [contains(text(), 'Счет получателя')] //..//input").wait_for(timeout=30000)
        page.locator("//p [contains(text(), 'Счет получателя')] //..//input").fill(target_account)
        page.locator("//p [contains(text(), 'Сумма перевода')] //..//label").fill('5.03')
        page.locator("//button[@class='custom-button custom-button--active']").wait_for(timeout=30000)
        page.locator("//button[@class='custom-button custom-button--active']").click()
        time.sleep(20)
    else:
    # Заполняем сумму и аккаунт
        page.locator("//p [contains(text(), 'Счет получателя')] //..//input").wait_for(timeout=30000)
        page.locator("//p [contains(text(), 'Счет получателя')] //..//input").fill(target_account)
        page.locator("//p [contains(text(), 'Сумма перевода')] //..//label").fill('5.03')
        page.locator("//button[@class='custom-button custom-button--active']").wait_for(timeout=30000)
        page.locator("//button[@class='custom-button custom-button--active']").click()
        time.sleep(20)
    # Проверка на ошибку счета
        # Явное ожидание появления ошибки на странице с таймаутом
    try:
        if page.locator("//span[contains(text(), 'Счет')]").is_visible():
            successful_accounts.append({"account_problema_s_schetom": target_account})
            browser_context.close()
        elif page.locator("//span[contains(text(), 'Внутренняя')]").is_visible():
            successful_accounts.append({"account_internal": target_account})
            browser_context.close()
        elif page.locator("//span[contains(text(), 'Оба счета должны быть в одной валюте')]").is_visible():
            successful_accounts.append({"account_CCY_problem": target_account})
            browser_context.close()
        elif page.locator("//span[contains(text(), 'Операция')]").is_visible():
            successful_accounts.append({"account_operaciya_nevozmojna": target_account})
            browser_context.close()
        else:
            # Если не найдены вышеуказанные ошибки, продолжаем выполнение сценария
            page.locator("//button[@class='custom-button custom-button--accept custom-button--active']").wait_for(
                timeout=30000)
            page.locator("//button[@class='custom-button custom-button--accept custom-button--active']").click()
            otp_page.login_in_system('1')
            time.sleep(3)
            page.locator("//a[@class='header-nav__link']").nth(1).wait_for(timeout=30000)
            page.locator("//a[@class='header-nav__link']").nth(1).click()
            successful_accounts.append({"account_no": target_account})  # Добавляем аккаунт в массив успешных записей
            time.sleep(1)  # Задержка для проверки результатов вручную
            browser_context.close()
    except Exception as e:
        logger.error(f"Ошибка при обработке счета: {e}")


    with open(SUCCESSFUL_ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        f.write('successful_accounts = [\n')
        for account in successful_accounts:
            f.write(f'    {account},\n')
        f.write(']\n')

