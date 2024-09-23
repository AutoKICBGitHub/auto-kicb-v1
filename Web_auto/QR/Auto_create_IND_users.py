import re
from faker import Faker
import random
import time
from playwright.sync_api import Playwright, sync_playwright
from transliterate import translit

# Инициализация Faker с русской локалью
fake = Faker('ru_RU')


def generate_kyrgyzstan_phone():
    """Генерация случайного номера телефона Кыргызстана"""
    operator_code = random.choice(['700', '701', '705', '707', '708', '777', '779', '755'])
    phone_number = f"{operator_code}{fake.random_number(digits=6, fix_len=True)}"
    return phone_number


def clear_and_fill_field(locator, text):
    """Функция для очистки поля и заполнения новым текстом"""
    locator.click()
    locator.fill('')
    locator.evaluate('el => el.value = ""')
    locator.type(text)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Переход на страницу
    page.goto("http://192.168.190.46:55556/admin-ui/auth")

    # Вход в систему
    page.get_by_label("Login").click()
    page.get_by_label("Login").fill("admin")
    page.get_by_label("Login").press("Tab")
    page.get_by_label("Password").fill("Protokol1")
    page.get_by_label("Password").press("Enter")

    # Навигация
    page.locator("div:nth-child(3) > div > .q-tree__arrow").click()
    page.locator("div:nth-child(4) > div > .q-tree__arrow").click()
    page.get_by_role("link", name="Работа с клиентами").click()

    # Поиск клиента
    page.get_by_placeholder("Поиск").click()
    page.get_by_placeholder("Поиск").fill("00375174")
    page.get_by_placeholder("Поиск").press("Enter")
    page.get_by_role("cell", name="00375174").click()

    # Добавление данных
    page.get_by_text("Добавить").click()
    time.sleep(1)
    page.get_by_label("Сотрудник ИП").click()

    # Генерация случайного имени на кириллице
    full_name_cyrillic = fake.name()

    # Транслитерация имени на латиницу
    full_name_latin = translit(full_name_cyrillic, 'ru', reversed=True)

    # Заполнение полей ФИО кириллицей и латиницей
    page.get_by_label("ФИО (кириллица)").clear()
    page.get_by_label("ФИО (кириллица)").fill(full_name_cyrillic)
    page.get_by_label("ФИО (латиница)").clear()
    page.get_by_label("ФИО (латиница)").fill(full_name_latin)

    # Генерация случайного номера телефона Кыргызстана
    phone_number = generate_kyrgyzstan_phone()
    page.get_by_label("Номер телефона").fill(phone_number)

    # Генерация случайной почты
    random_email = fake.email()
    page.get_by_label("Почта").fill(random_email)

    # Кодовое слово
    page.get_by_label("Кодовое слово").click()
    page.get_by_label("Кодовое слово").fill("test")

    # Печать заявки
    while True:
        page.get_by_role("button", name="Распечатать заявку на подключение").click()

        # Блокировка вызова печати
        page.evaluate("""window.print = () => { console.log('Попытка печати заблокирована'); };""")
        page.get_by_role("button", name="Распечатать").click()

        try:
            # Ждем появления сообщения "Пользователь уже существует"
            if page.locator("text=Пользователь уже существует").is_visible(timeout=6000):
                print("Пользователь уже существует, генерируем новый номер...")
                page.get_by_label("Сотрудник ИП").click()

                # Генерация нового номера телефона
                new_phone_number = generate_kyrgyzstan_phone()

                # Очищаем поле и вставляем новый номер телефона
                phone_field = page.get_by_label("Номер телефона")
                clear_and_fill_field(phone_field, new_phone_number)

                page.get_by_role("button", name="Распечатать заявку на подключение").click()
                page.evaluate("""window.print = () => { console.log('Попытка печати заблокирована'); };""")
                page.get_by_role("button", name="Распечатать").click()

                # Загрузка файла
                uploader = page.wait_for_selector("//input[@type='file']")
                uploader.set_input_files(r"C:\project_kicb\WebAutoTests\QR\image-with-layout (2).png")
                page.get_by_role("button", name="Установить статус заявки").click()
                time.sleep(1)
                # Выбор статуса заявки
                page.locator("div").filter(has_text=re.compile(r"^Выберите статус$")).first.click()
                page.get_by_text("На верификации").click()
                page.get_by_role("button", name="OK").click()
                time.sleep(1)
                # Установка статуса на "Принят"
                page.get_by_role("button", name="Установить статус заявки").click()
                page.locator(
                    ".q-dialog-plugin > label > .q-field__inner > .q-field__control > .q-field__control-container > .q-field__native").first.click()
                page.get_by_role("option", name="Принят").locator("div").nth(1).click()
                page.get_by_role("button", name="OK").click()

                # Закрытие браузера
                context.close()
                browser.close()
            else:
                break  # Если уведомление не появилось, выходим из цикла
        except:
            break  # Если не удалось обнаружить уведомление, продолжаем выполнение

    # Загрузка файла
    uploader = page.wait_for_selector("//input[@type='file']")
    uploader.set_input_files(r"C:\project_kicb\WebAutoTests\QR\image-with-layout (2).png")
    page.get_by_role("button", name="Установить статус заявки").click()
    time.sleep(1)
    # Выбор статуса заявки
    page.locator("div").filter(has_text=re.compile(r"^Выберите статус$")).first.click()
    page.get_by_text("На верификации").click()
    page.get_by_role("button", name="OK").click()
    time.sleep(1)
    # Установка статуса на "Принят"
    page.get_by_role("button", name="Установить статус заявки").click()
    page.locator(
        ".q-dialog-plugin > label > .q-field__inner > .q-field__control > .q-field__control-container > .q-field__native").first.click()
    page.get_by_role("option", name="Принят").locator("div").nth(1).click()
    page.get_by_role("button", name="OK").click()

    # Закрытие браузера
    context.close()
    browser.close()


def run_150_times():
    with sync_playwright() as playwright:
        for i in range(150):
            print(f"Запуск #{i + 1}")
            try:
                run(playwright)
            except Exception as e:
                print(f"Произошла ошибка на запуске #{i + 1}: {e}")
            finally:
                time.sleep(1)  # Пауза между запусками


if __name__ == "__main__":
    run_150_times()
