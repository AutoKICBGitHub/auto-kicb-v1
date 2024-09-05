import time
import random
import pytest
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright


@pytest.fixture(scope="session")
def load_times():
    return []


def run(playwright: Playwright, run_number: int, load_times: list) -> None:
    # Запуск браузера в headless режиме
    browser = playwright.chromium.launch(headless=True)

    # Создание нового контекста браузера (инкогнито режим)
    context = browser.new_context()  # Контекст браузера по умолчанию инкогнито

    page = context.new_page()

    random_param = random.randint(1, 100000)
    print(f"[Запуск {run_number}] Сгенерированный параметр для обхода кеша: {random_param}")

    test_start_time = datetime.now()
    print(f"[Запуск {run_number}] Тест начался: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Переход на страницу с добавленным случайным параметром для обхода кэша
    page.goto(f"https://newibanktest.kicb.net/?nocache={random_param}")
    page.wait_for_selector("input[type=\"text\"]")
    page.locator("input[type=\"text\"]").fill("aselm")
    page.locator("input[type=\"text\"]").press("Tab")

    page.wait_for_selector("input[type=\"password\"]")
    page.locator("input[type=\"password\"]").fill("password1")
    time.sleep(2)
    page.locator("button:has-text('Войти')").click()

    page.wait_for_selector(".confirm-otp__input")
    print(f"[Запуск {run_number}] OTP ввод открыт.")

    otp_code = "111111"

    for index, digit in enumerate(otp_code):
        page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)

    print(f"[Запуск {run_number}] OTP введен. Начало замера времени.")

    start_time = time.time()

    try:
        # Ждем, пока страница загрузит основной контент после OTP
        page.wait_for_selector("element_that_confirms_page_is_loaded", timeout=15000)  # Замените селектором элемента, подтверждающим загрузку

        load_time = time.time() - start_time
        load_times.append(load_time)
        print(f"[Запуск {run_number}] Время загрузки страницы после ввода OTP: {load_time:.2f} секунд")

        page.wait_for_selector("div.history-element__title:has-text('Оплата по QR')", timeout=15000)

        # Переход на вкладку История
        print(f"[Запуск {run_number}] Нажатие на вкладку 'История'")
        page.locator("a[href='#/history']").click()

        # Ждем появления элемента "Оплата по QR" на странице истории
        page.wait_for_selector("div.history-element__title:has-text('Оплата по QR')", timeout=15000)
        print(f"[Запуск {run_number}] Оплата по QR элемент найден.")

        # Переход обратно на вкладку Счета
        print(f"[Запуск {run_number}] Возврат на вкладку 'Счета'")
        page.locator("a[href='#/']").click()

        # Ждем загрузки страницы Счета (ожидание специфического элемента)
        page.wait_for_selector("element_on_accounts_page", timeout=15000)  # Замените элементом на странице Счета
        print(f"[Запуск {run_number}] Возврат на 'Счета' выполнен")

    except Exception as e:
        print(f"[Запуск {run_number}] Ошибка при ожидании: {e}")
        page.screenshot(path=f"error_{run_number}.png")

    context.close()
    browser.close()

    test_end_time = datetime.now()
    print(f"[Запуск {run_number}] Тест завершился: {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[Запуск {run_number}] Продолжительность теста: {test_end_time - test_start_time}")


@pytest.mark.parametrize("run_number", range(1, 51))
def test_sequential_runs(run_number, load_times):
    with sync_playwright() as playwright:
        run(playwright, run_number, load_times)


def test_average_load_time(load_times):
    if load_times:
        average_load_time = sum(load_times) / len(load_times)
        print(f"Среднее время загрузки страницы: {average_load_time:.2f} секунд")

        for i, load_time in enumerate(load_times, start=1):
            assert load_time < 120, f"Время загрузки страницы на запуске {i} слишком велико"
