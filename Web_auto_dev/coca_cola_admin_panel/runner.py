import time
from playwright.sync_api import sync_playwright
import random
import sys
import os
import sys
sys.path.append("C:/project_kicb/Web_auto_dev/coca_cola_admin_panel")

from corp_ids import corp_ids
from counterparty_ids import counterparty_ids



# Конфигурация
URL = "http://192.168.190.46:55556/admin-ui/"
LOGIN = "admin"
PASSWORD = "Protokol1"

# Логирование результатов в Python-файл
RESULTS_FILE = "results.py"


def log_result(corp_id, counterparty_id, status, error_message=None):
    """Добавляет результат в файл `results.py`."""
    try:
        with open(RESULTS_FILE, "a") as file:
            file.write(
                f"results.append({{'corp_id': {corp_id}, 'counterparty_id': {counterparty_id}, "
                f"'status': '{status}', 'error': {repr(error_message)}}})\n"
            )
        print(f"Результат записан: corp_id={corp_id}, counterparty_id={counterparty_id}, status={status}")
    except Exception as e:
        print(f"Ошибка записи результата: {e}")


def check_for_error(page):
    """Проверяет наличие всплывающей ошибки на странице."""
    try:
        # Ждём появления элемента ошибки (максимум 2 секунды)
        error_notification = page.wait_for_selector("//div[@class='q-notification__message col']", timeout=2000)
        if error_notification:
            error_text = error_notification.inner_text()
            print(f"Обнаружена ошибка: {error_text}")
            return error_text
    except Exception:
        # Если элемент не появляется, игнорируем
        pass
    return None


def run(playwright, corp_id, counterparty_id):
    browser = None
    context = None
    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"Начало теста: corp_id={corp_id}, counterparty_id={counterparty_id}")

            # Переход на страницу
            try:
                page.goto(URL)
                print("Переход на страницу выполнен")
            except Exception as e:
                raise Exception(f"Ошибка перехода на страницу: {e}")

            # Вход в систему
            try:
                page.get_by_label("Login").click()
                page.get_by_label("Login").fill(LOGIN)
                page.get_by_label("Login").press("Tab")
                page.get_by_label("Password").fill(PASSWORD)
                page.get_by_label("Password").press("Enter")
                print("Вход в систему выполнен")
            except Exception as e:
                raise Exception(f"Ошибка входа в систему: {e}")

            # Переход в настройки клиентов
            try:
                page.locator("//div[contains(text(), 'Прямое дебетование')]").click()
                page.locator("//a[contains(text(), 'Настройка клиентов')]").click()
                print("Переход в 'Настройка клиентов' выполнен")
            except Exception as e:
                raise Exception(f"Ошибка перехода в 'Настройка клиентов': {e}")

            # Поиск и выбор корпорации
            try:
                page.locator("//input[@placeholder='Поиск']").fill(f"{corp_id}")
                page.locator("//input[@placeholder='Поиск']").press("Enter")
                page.locator(f"//td[contains(text(), '{corp_id}')]").click()
                print(f"Корпорация {corp_id} выбрана")
            except Exception as e:
                raise Exception(f"Ошибка выбора корпорации {corp_id}: {e}")

            # Добавление контрагента
            try:
                page.locator("//span[contains(text(), 'Добавить')]").click()
                time.sleep(1)
                page.locator("//div[contains(text(), 'Выбрать счет клиента')]").click(force=True)
                page.locator("//div[@class='q-item__label']").nth(0).wait_for(timeout=10000)
                page.locator("//div[@class='q-item__label']").nth(0).click(force=True)
                print("Счет клиента выбран")
            except Exception as e:
                raise Exception(f"Ошибка выбора счета клиента: {e}")

            # Проверяем наличие ошибки
            error_message = check_for_error(page)
            if error_message:
                log_result(corp_id, counterparty_id, "error", error_message)
                return

            # Выбор контрагента
            try:
                page.locator("//div[contains(text(), 'Поиск по')]").click(force=True)
                page.locator("//div[contains(text(), 'ID клиента')]").click(force=True)
                page.locator("//input[@placeholder='Поиск']").fill(f"{counterparty_id}")
                page.locator("//input[@placeholder='Поиск']").press("Enter")
                time.sleep(1)
                page.locator("//div[contains(text(), 'Выбрать счет контрагента')]").click(force=True)
                page.locator("//div[@class='q-item__label']").nth(0).click(force=True)
                print(f"Контрагент {counterparty_id} выбран")
            except Exception as e:
                raise Exception(f"Ошибка выбора контрагента {counterparty_id}: {e}")

            # Проверяем наличие ошибки
            error_message = check_for_error(page)
            if error_message:
                log_result(corp_id, counterparty_id, "error", error_message)
                return

            # Ввод номера контрагента и сохранение
            try:
                random_number = str(random.randint(100000, 999999))
                page.locator("//input[@placeholder='Номер контрагента']").fill(random_number)
                page.locator("//span[contains(text(), 'Сохранить')]").click()
                print("Данные сохранены")
            except Exception as e:
                raise Exception(f"Ошибка сохранения данных: {e}")

            # Проверка уведомления об ошибке
            error_message = check_for_error(page)
            if error_message:
                log_result(corp_id, counterparty_id, "error", error_message)
            else:
                log_result(corp_id, counterparty_id, "success")
                print(f"Успешное завершение для corp_id={corp_id}, counterparty_id={counterparty_id}")

        except Exception as e:
            # Логируем любые неожиданные ошибки
            log_result(corp_id, counterparty_id, "error", str(e))
            print(f"Общая ошибка: corp_id={corp_id}, counterparty_id={counterparty_id}, ошибка={e}")

    finally:
        try:
            if context:
                context.close()
            if browser:
                browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    playwright_instance = None
    try:
        with open(RESULTS_FILE, "w") as file:
            file.write("results = []\n")

        playwright_instance = sync_playwright().start()
        for corp_id in corp_ids:
            for counterparty_id in counterparty_ids:
                try:
                    run(playwright_instance, corp_id, counterparty_id)
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\nПрограмма остановлена пользователем")
                    sys.exit(0)
                except Exception as e:
                    print(f"Ошибка при обработке corp_id={corp_id}, counterparty_id={counterparty_id}: {e}")
                    continue
    finally:
        if playwright_instance:
            try:
                playwright_instance.stop()
            except Exception as e:
                print(f"Ошибка при закрытии playwright: {e}")
