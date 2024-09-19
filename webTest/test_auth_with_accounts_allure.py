import time
import random
import pytest
import allure
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright


@pytest.fixture(scope="session")
def load_times():
    return []


@allure.step("Запуск теста {run_number}")
def run(playwright: Playwright, run_number: int, load_times: list) -> None:
    with allure.step(f"Запуск браузера в headless режиме, запуск #{run_number}"):
        # Запуск браузера в headless режиме
        browser = playwright.chromium.launch(headless=True)

        # Создание нового контекста браузера (инкогнито режим)
        context = browser.new_context()

        page = context.new_page()

    random_param = random.randint(1, 100000)
    allure.attach(body=f"Сгенерированный параметр для обхода кэша: {random_param}", name="Параметр")

    test_start_time = datetime.now()
    allure.attach(body=f"Тест начался: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}", name="Время начала")

    # Переход на страницу с добавленным случайным параметром для обхода кэша
    page.goto(f"https://newibanktest.kicb.net/?nocache={random_param}")
    page.wait_for_selector("input[type=\"text\"]")

    with allure.step("Заполнение поля логина"):
        page.locator("input[type=\"text\"]").fill("aselm")
        page.locator("input[type=\"text\"]").press("Tab")

    page.wait_for_selector("input[type=\"password\"]")

    with allure.step("Заполнение поля пароля"):
        page.locator("input[type=\"password\"]").fill("password1")
        time.sleep(2)
        page.locator("button:has-text('Войти')").click()

    with allure.step("Ожидание открытия OTP ввода"):
        page.wait_for_selector(".confirm-otp__input")
        otp_code = "111111"

        for index, digit in enumerate(otp_code):
            page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)

    start_time = time.time()

    with allure.step("Ожидание текста после ввода OTP"):
        try:
            page.wait_for_selector(f"text=271 248.24", timeout=120000)
            load_time = time.time() - start_time
            load_times.append(load_time)
            allure.attach(body=f"Время загрузки страницы: {load_time:.2f} секунд", name="Время загрузки")
        except Exception as e:
            allure.attach(page.screenshot(), name=f"Ошибка на запуске #{run_number}",
                          attachment_type=allure.attachment_type.PNG)
            allure.attach(body=str(e), name="Ошибка")

    context.close()
    browser.close()

    test_end_time = datetime.now()
    allure.attach(body=f"Тест завершился: {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}", name="Время окончания")
    allure.attach(body=f"Продолжительность теста: {test_end_time - test_start_time}", name="Продолжительность")


@pytest.mark.parametrize("run_number", range(1, 151))
@allure.title("Запуск #{run_number}")
@allure.description("Запуск теста с последовательной загрузкой страницы и вводом OTP")
def test_sequential_runs(run_number, load_times):
    with sync_playwright() as playwright:
        run(playwright, run_number, load_times)


@allure.step("Расчет среднего времени загрузки")
def test_average_load_time(load_times):
    if load_times:
        average_load_time = sum(load_times) / len(load_times)
        allure.attach(body=f"Среднее время загрузки страницы: {average_load_time:.2f} секунд",
                      name="Среднее время загрузки")

        for i, load_time in enumerate(load_times, start=1):
            assert load_time < 120, f"Время загрузки страницы на запуске {i} слишком велико"


# cd C:\project_kicb\webTest\
# pytest --alluredir=allure-results .\test_auth_with_accounts_allure.py
# allure serve allure-results

