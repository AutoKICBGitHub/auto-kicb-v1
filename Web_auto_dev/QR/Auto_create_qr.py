import time
import random
import pytest
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
from faker import Faker  # Импорт Faker


@pytest.fixture(scope="session")
def load_times():
    return []


def run(playwright: Playwright, run_number: int, load_times: list) -> None:
    fake = Faker()  # Инициализация Faker
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    random_param = random.randint(1, 100000)
    print(f"[Запуск {run_number}] Сгенерированный параметр для обхода кеша: {random_param}")

    test_start_time = datetime.now()
    print(f"[Запуск {run_number}] Тест начался: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    page.goto(f"https://newibanktest.kicb.net/?nocache={random_param}")
    page.wait_for_selector("input[type=\"text\"]")
    load_times.append((datetime.now() - test_start_time).total_seconds())

    page.locator("input[type=\"text\"]").fill("00885_14")
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

    print(f"[Запуск {run_number}]")

    # Ожидание загрузки элементов и выбор случайного элемента
    page.wait_for_selector("//div[@class='expand-data']", timeout=60000)
    random_card = random.randint(0, 11)
    page.locator("//div[@class='expand-data']").nth(random_card).click()  # Выбор случайной карты

    # Ожидание и выбор нужной ссылки из account-details
    page.locator("//div[@class='account-details__link']").nth(3).click()

    # Генерация случайных имени и описания
    random_name = fake.name()
    random_description = fake.text(max_nb_chars=25)  # Ограничение по количеству символов

    # Заполнение полей формы
    page.locator("//label").nth(0).fill(random_name)
    page.locator("//label").nth(1).fill(random_description)

    # Нажатие на кнопку "Сохранить"
    page.locator("//button[@class ='custom-button']").nth(0).click()

    # Действия после сохранения
    page.locator("//div[@class='btn-cancel']").click()

    # Установить чекбокс
    page.locator("//div[@class='q-checkbox__bg absolute']").nth(0).click()

    # Нажатие на пятую кнопку в списке кнопок
    page.locator("//button").nth(5).click()
    page.locator("//button[@class ='custom-button']").nth(2).click()


    time.sleep(1)

    context.close()
    browser.close()

    test_end_time = datetime.now()
    print(f"[Запуск {run_number}] Тест завершился: {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[Запуск {run_number}] Продолжительность теста: {test_end_time - test_start_time}")


@pytest.mark.parametrize("run_number", range(1, 150))
def test_sequential_runs(run_number, load_times):
    with sync_playwright() as playwright:
        run(playwright, run_number, load_times)


def test_average_load_time(load_times):
    if load_times:
        average_load_time = sum(load_times) / len(load_times)
        print(f"Среднее время загрузки страницы: {average_load_time:.2f} секунд")

        for i, load_time in enumerate(load_times, start=1):
            assert load_time < 120, f"Время загрузки страницы на запуске {i} слишком велико"
